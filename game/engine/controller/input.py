"""Runtime event processing and action buffering."""

from collections import deque

import pygame
import pygame._sdl2.controller

from .bindings import ALL_ACTIONS, BindingStore
from .devices import controller_types, discover_controllers
from .models import AxesSnapshot, InputAction, InputFrame


class Controller:
    """Translate device input into semantic game actions."""

    BINDINGS_VERSION = BindingStore.VERSION

    def __init__(self, bindings_path="config/input_bindings.json"):
        self.buffer_lifetime = 10
        self.ui_repeat_delay = 12
        self.ui_repeat_interval = 6
        self.ui_nav_threshold = 0.85
        self.move_deadzone = 0.2
        self.look_deadzone = 0.1
        self.trigger_threshold = 0.5
        self.bindings = BindingStore(bindings_path)
        self.pending_rebind = None
        self.held_buttons = set()
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

    # Compatibility properties keep existing game code and options UI stable.
    @property
    def bindings_path(self):
        return self.bindings.path

    @property
    def keyboard_buttons(self):
        return self.bindings.keyboard_buttons

    @property
    def keyboard_directions(self):
        return self.bindings.keyboard_directions

    @property
    def controller_buttons(self):
        return self.bindings.controller_buttons

    @property
    def controller_directions(self):
        return self.bindings.controller_directions

    def bindings_data(self):
        return self.bindings.data()

    def save_bindings(self):
        self.bindings.save()

    def load_bindings(self):
        return self.bindings.load()

    def reset_bindings(self):
        self.bindings.reset()

    def rebind_keyboard(self, action, key):
        self.bindings.rebind("keyboard", action, key)

    def rebind_controller(self, action, button):
        self.bindings.rebind("controller", action, button)

    def binding_name(self, device, action):
        return self.bindings.binding_name(device, action)

    def begin_rebind(self, action):
        if action not in ALL_ACTIONS:
            raise ValueError(f"Unknown input action: {action}")
        self.pending_rebind = action

    def cancel_rebind(self):
        self.pending_rebind = None

    def update(self, events, dt):
        self._update_buffer(dt)
        frame_pressed, frame_released = set(), set()
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

    def rumble(self, duration=1000):
        for controller in self.controllers:
            controller.rumble(0, 0.7, duration)

    def is_held(self, button_name):
        return button_name in self.held_buttons

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
            InputAction(
                name,
                pressed,
                released,
                axes or self.frame.axes,
                lifetime,
            )
        )

    def _handle_event(self, event, frame_pressed, frame_released):
        if self.pending_rebind is not None and self._capture_rebind(event):
            return
        if event.type in (pygame.CONTROLLERDEVICEADDED, pygame.CONTROLLERDEVICEREMOVED):
            self.update_controller()
        elif event.type == pygame.KEYDOWN:
            self.prompt_type = "keyboard"
            self._handle_down(
                event.key,
                self.keyboard_buttons,
                self.keyboard_directions,
                frame_pressed,
            )
        elif event.type == pygame.KEYUP:
            self._handle_up(
                event.key,
                self.keyboard_buttons,
                self.keyboard_directions,
                frame_released,
            )
        elif event.type == pygame.CONTROLLERBUTTONDOWN:
            self._use_controller_prompt(getattr(event, "instance_id", None))
            self._handle_down(
                event.button,
                self.controller_buttons,
                self.controller_directions,
                frame_pressed,
            )
        elif event.type == pygame.CONTROLLERBUTTONUP:
            self._handle_up(
                event.button,
                self.controller_buttons,
                self.controller_directions,
                frame_released,
            )

    def _handle_down(self, input_id, buttons, directions, frame_pressed):
        action = buttons.get(input_id)
        if action and action not in self.held_buttons:
            self.held_buttons.add(action)
            frame_pressed.add(action)
        elif direction := directions.get(input_id):
            self.held_directions.add(direction)

    def _handle_up(self, input_id, buttons, directions, frame_released):
        action = buttons.get(input_id)
        if action and action in self.held_buttons:
            self.held_buttons.discard(action)
            frame_released.add(action)
        elif direction := directions.get(input_id):
            self.held_directions.discard(direction)

    def _sample_axes(self):
        keys = pygame.key.get_pressed()
        move_x = move_y = look_x = look_y = 0
        for key, direction in self.keyboard_directions.items():
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
        for name in frame_released:
            self.enqueue_action(name, released=True, axes=self.frame.axes)

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

    def _capture_rebind(self, event):
        if event.type == pygame.KEYDOWN:
            self._finish_rebind("keyboard", event.key)
            return True
        if event.type == pygame.CONTROLLERBUTTONDOWN:
            self._finish_rebind("controller", event.button)
            self._use_controller_prompt(getattr(event, "instance_id", None))
            return True
        return False

    def _finish_rebind(self, device, input_id):
        action = self.pending_rebind
        self.bindings.rebind(device, action, input_id)
        self.pending_rebind = None
        result = InputAction("binding_captured", pressed=True, axes=self.frame.axes)
        result.meta.update(action=action, device=device, input_id=input_id)
        self.input_buffer.append(result)

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
