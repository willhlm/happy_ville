"""Runtime event processing and action buffering."""

from collections import deque

import pygame
import pygame._sdl2.controller

from .devices import controller_types, discover_controllers
from .models import AxesSnapshot, InputAction, InputFrame


KEYBOARD_DIRECTIONS = {
    pygame.K_RIGHT: "right", pygame.K_LEFT: "left",
    pygame.K_UP: "up", pygame.K_DOWN: "down",
}


class Controller:
    """Translate device input into semantic game actions."""

    def __init__(self):
        self.buffer_lifetime = 10
        self.ui_repeat_delay = 12
        self.ui_repeat_interval = 6
        self.ui_nav_threshold = 0.85
        self.move_deadzone = 0.2
        self.look_deadzone = 0.1
        self.trigger_threshold = 0.5
        self.pending_capture = False
        self.held_buttons = set()
        self.held_controls = set()
        self._frame_controls = {}
        self.held_directions = set()
        self.input_buffer = deque()
        self.nav_repeat = {
            direction: {"active": False, "timer": 0}
            for direction in ("up", "down", "left", "right")
        }
        self.left_trigger_value = 0.0
        self.right_trigger_value = 0.0
        self.right_trigger_pressed = False
        self.raw_axes = AxesSnapshot((0, 0), (0, 0), (0, 0), 0, 0)
        self.frame = InputFrame(self.raw_axes, frozenset(), frozenset(), frozenset(), 0)
        pygame._sdl2.controller.init()
        self.controllers = []
        self.controller_types = {}
        self.prompt_type = "keyboard"
        self.update_controller()

    def begin_capture(self):
        """Capture the next keyboard key or controller button."""
        self.pending_capture = True

    def cancel_capture(self):
        self.pending_capture = False

    def update(self, events, dt):
        self._update_buffer(dt)
        frame_pressed, frame_released = set(), set()
        self._frame_controls = {}
        for event in events:
            self._handle_event(event, frame_pressed, frame_released)
        axes = self._sample_axes()
        self.raw_axes = axes
        self._update_trigger_action(frame_pressed, frame_released, axes.r_trigger)
        self.frame = InputFrame(
            axes,
            frozenset(frame_pressed),
            frozenset(frame_released),
            frozenset(self.held_buttons),
            dt,
        )
        self._enqueue_button_actions(frame_pressed, frame_released)
        self._enqueue_navigation_actions(dt)

    def update_controller(self):
        self.controllers = discover_controllers()
        self.controller_types = controller_types(self.controllers)
        if (
            self.prompt_type != "keyboard"
            and self.prompt_type not in self.controller_types.values()
        ):
            self.prompt_type = "keyboard"

    def initiate_controls(self):
        self.controllers = discover_controllers()

    def rumble(self, duration=1000, amplitude=1.0):
        amplitude = max(0.0, min(1.0, amplitude))
        if amplitude == 0:
            return
        for controller in self.controllers:
            controller.rumble(0, 0.7 * amplitude, duration)

    def is_held(self, button_name):
        return button_name in self.held_buttons

    def is_control_held(self, control_id):
        return control_id in self.held_controls

    def get_inputs(self):
        return list(self.input_buffer)

    def clear_buffer(self):
        self.input_buffer.clear()

    def enqueue_action(
        self, name, pressed=False, released=False, axes=None, lifetime=None
    ):
        if lifetime is None:
            lifetime = self.buffer_lifetime
        self.input_buffer.append(
            InputAction(name, pressed, released, axes or self.frame.axes, lifetime,)
        )

    def _handle_event(self, event, frame_pressed, frame_released):
        if self.pending_capture and self._capture_source(event):
            return
        if event.type in (pygame.CONTROLLERDEVICEADDED, pygame.CONTROLLERDEVICEREMOVED):
            self.update_controller()
        elif event.type == pygame.KEYDOWN:
            self.prompt_type = "keyboard"
            self._handle_down(
                f"keyboard:{event.key}",
                event.key,
                frame_pressed,
            )
        elif event.type == pygame.KEYUP:
            self._handle_up(
                f"keyboard:{event.key}",
                event.key,
                frame_released,
            )
        elif event.type == pygame.CONTROLLERBUTTONDOWN:
            self._use_controller_prompt(getattr(event, "instance_id", None))
            self._handle_down(
                f"controller:{event.button}",
                event.button,
                frame_pressed,
            )
        elif event.type == pygame.CONTROLLERBUTTONUP:
            self._handle_up(
                f"controller:{event.button}",
                event.button,
                frame_released,
            )

    def _handle_down(self, control_id, input_id, frame_pressed):
        if direction := KEYBOARD_DIRECTIONS.get(input_id):
            self.held_directions.add(direction)
        if control_id not in self.held_controls:
            self.held_controls.add(control_id)
            frame_pressed.add(control_id)
            self._frame_controls[("pressed", control_id)] = control_id

    def _handle_up(self, control_id, input_id, frame_released):
        if direction := KEYBOARD_DIRECTIONS.get(input_id):
            self.held_directions.discard(direction)
        if control_id in self.held_controls:
            self.held_controls.discard(control_id)
            frame_released.add(control_id)
            self._frame_controls[("released", control_id)] = control_id

    def _sample_axes(self):
        keys = pygame.key.get_pressed()
        move_x = move_y = look_x = look_y = 0
        for key, direction in KEYBOARD_DIRECTIONS.items():
            if self._key_is_pressed(keys, key):
                move_x, move_y = self._apply_direction(direction, move_x, move_y)
        for controller in self.controllers:
            left_x = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_LEFTX)
            )
            left_y = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_LEFTY)
            )
            right_x = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTX)
            )
            right_y = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTY)
            )
            self.left_trigger_value = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_TRIGGERLEFT)
            )
            self.right_trigger_value = self.normalize_axis(
                controller.get_axis(pygame.CONTROLLER_AXIS_TRIGGERRIGHT)
            )
            if any(
                (
                    abs(left_x) > self.move_deadzone,
                    abs(left_y) > self.move_deadzone,
                    abs(right_x) > self.look_deadzone,
                    abs(right_y) > self.look_deadzone,
                    self.left_trigger_value > self.trigger_threshold,
                    self.right_trigger_value > self.trigger_threshold,
                )
            ):
                self._use_controller_prompt(controller.id)
            if abs(left_x) > self.move_deadzone:
                move_x = left_x
            if abs(left_y) > self.move_deadzone:
                move_y = left_y
            if abs(right_x) > self.look_deadzone:
                look_x = right_x
            if abs(right_y) > self.look_deadzone:
                look_y = right_y
        dpad_x = int("right" in self.held_directions) - int(
            "left" in self.held_directions
        )
        dpad_y = int("down" in self.held_directions) - int("up" in self.held_directions)
        return AxesSnapshot(
            (move_x, move_y),
            (look_x, look_y),
            (dpad_x, dpad_y),
            self.left_trigger_value,
            self.right_trigger_value,
        )

    def _update_trigger_action(
        self, frame_pressed, frame_released, right_trigger_value
    ):
        is_pressed = right_trigger_value > self.trigger_threshold
        if is_pressed and not self.right_trigger_pressed:
            self.held_buttons.add("rt")
            frame_pressed.add("rt")
        elif not is_pressed and self.right_trigger_pressed:
            self.held_buttons.discard("rt")
            frame_released.add("rt")
        self.right_trigger_pressed = is_pressed

    def _enqueue_button_actions(self, frame_pressed, frame_released):
        for name in frame_pressed:
            self.enqueue_action(name, pressed=True, axes=self.frame.axes)
            self.input_buffer[-1].meta["physical_input"] = self._frame_controls.get(
                ("pressed", name)
            )
        for name in frame_released:
            self.enqueue_action(name, released=True, axes=self.frame.axes)
            self.input_buffer[-1].meta["physical_input"] = self._frame_controls.get(
                ("released", name)
            )

    def _enqueue_navigation_actions(self, dt):
        active = {
            "up": self.frame.axes.dpad[1] < 0
            or self.frame.axes.move[1] < -self.ui_nav_threshold,
            "down": self.frame.axes.dpad[1] > 0
            or self.frame.axes.move[1] > self.ui_nav_threshold,
            "left": self.frame.axes.dpad[0] < 0
            or self.frame.axes.move[0] < -self.ui_nav_threshold,
            "right": self.frame.axes.dpad[0] > 0
            or self.frame.axes.move[0] > self.ui_nav_threshold,
        }
        for direction, is_active in active.items():
            state = self.nav_repeat[direction]
            if not is_active:
                state.update(active=False, timer=0)
            elif not state["active"]:
                self.enqueue_action(direction, pressed=True, axes=self.frame.axes)
                state.update(active=True, timer=self.ui_repeat_delay)
            else:
                state["timer"] -= dt
                if state["timer"] <= 0:
                    self.enqueue_action(direction, pressed=True, axes=self.frame.axes)
                    state["timer"] = self.ui_repeat_interval

    def _update_buffer(self, dt):
        retained = deque()
        while self.input_buffer:
            action = self.input_buffer.popleft()
            action.update(dt)
            if not action.is_done:
                retained.append(action)
        self.input_buffer = retained

    def _capture_source(self, event):
        if event.type == pygame.KEYDOWN:
            source = f"keyboard:{event.key}"
            device, input_id = "keyboard", event.key
        elif event.type == pygame.CONTROLLERBUTTONDOWN:
            source = f"controller:{event.button}"
            device, input_id = "controller", event.button
            self._use_controller_prompt(getattr(event, "instance_id", None))
        else:
            return False

        self.pending_capture = False
        result = InputAction("binding_captured", pressed=True, axes=self.frame.axes)
        result.meta.update(source_action=source, device=device, input_id=input_id)
        self.input_buffer.append(result)
        return True

    def _use_controller_prompt(self, instance_id):
        if controller_type := self.controller_types.get(instance_id):
            self.prompt_type = controller_type

    @staticmethod
    def _apply_direction(direction, move_x, move_y):
        if direction == "right":
            return 1, move_y
        if direction == "left":
            return -1, move_y
        if direction == "up":
            return move_x, -1
        if direction == "down":
            return move_x, 1
        return move_x, move_y

    @staticmethod
    def _key_is_pressed(keys, key):
        try:
            return keys[key]
        except (IndexError, KeyError):
            return False

    @staticmethod
    def normalize_axis(value):
        return value / 32768.0
