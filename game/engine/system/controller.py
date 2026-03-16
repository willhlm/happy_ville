from collections import deque
from dataclasses import dataclass

import pygame
import pygame._sdl2.controller

@dataclass(frozen=True)
class AxesSnapshot:
    move: tuple[float, float]
    look: tuple[float, float]
    dpad: tuple[int, int]
    l_trigger: float
    r_trigger: float

@dataclass(frozen=True)
class InputFrame:
    axes: AxesSnapshot
    pressed: frozenset[str]
    released: frozenset[str]
    held: frozenset[str]
    dt: float

class InputAction:
    def __init__(self, name, pressed=False, released=False, axes=None, lifetime=10):
        self.name = name
        self.pressed = pressed
        self.released = released
        self.axes = axes or AxesSnapshot((0, 0), (0, 0), (0, 0), 0, 0)
        self.lifetime = lifetime
        self.meta = {}
        self.is_done = False

    def update(self, dt):
        if self.is_done:
            return
        self.lifetime -= dt
        if self.lifetime < 0:
            self.processed()

    def processed(self):
        self.is_done = True

class Controller:
    def __init__(self):
        self.buffer_lifetime = 10
        self.ui_repeat_delay = 12
        self.ui_repeat_interval = 6
        self.ui_nav_threshold = 0.85
        self.move_deadzone = 0.2
        self.look_deadzone = 0.1
        self.trigger_threshold = 0.5

        self.keyboard_buttons = {
            pygame.K_ESCAPE: "start",
            pygame.K_TAB: "rb",
            pygame.K_SPACE: "a",
            pygame.K_t: "y",
            pygame.K_e: "b",
            pygame.K_f: "x",
            pygame.K_g: "y",
            pygame.K_i: "select",
            pygame.K_LSHIFT: "lb",
            pygame.K_RETURN: "return",
        }
        self.keyboard_directions = {
            pygame.K_RIGHT: "right",
            pygame.K_LEFT: "left",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        self.controller_buttons = {
            pygame.CONTROLLER_BUTTON_A: "a",
            pygame.CONTROLLER_BUTTON_B: "b",
            pygame.CONTROLLER_BUTTON_X: "x",
            pygame.CONTROLLER_BUTTON_Y: "y",
            pygame.CONTROLLER_BUTTON_START: "start",
            pygame.CONTROLLER_BUTTON_BACK: "select",
            pygame.CONTROLLER_BUTTON_LEFTSHOULDER: "lb",
            pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: "rb",
            pygame.CONTROLLER_BUTTON_LEFTSTICK: "ls",
            pygame.CONTROLLER_BUTTON_RIGHTSTICK: "rs",
            pygame.CONTROLLER_BUTTON_GUIDE: "guide",
        }
        self.controller_directions = {
            pygame.CONTROLLER_BUTTON_DPAD_UP: "up",
            pygame.CONTROLLER_BUTTON_DPAD_DOWN: "down",
            pygame.CONTROLLER_BUTTON_DPAD_LEFT: "left",
            pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "right",
        }

        self.held_buttons = set()
        self.held_directions = set()
        self.input_buffer = deque()
        self.nav_repeat = {
            "up": {"active": False, "timer": 0},
            "down": {"active": False, "timer": 0},
            "left": {"active": False, "timer": 0},
            "right": {"active": False, "timer": 0},
        }

        self.left_trigger_value = 0.0
        self.right_trigger_value = 0.0
        self.right_trigger_pressed = False

        self.raw_axes = AxesSnapshot((0, 0), (0, 0), (0, 0), 0, 0)
        self.frame = InputFrame(
            axes=self.raw_axes,
            pressed=frozenset(),
            released=frozenset(),
            held=frozenset(),
            dt=0,
        )

        pygame._sdl2.controller.init()
        self.controllers = []
        self.initiate_controls()
        self.get_controller_type()

    def update(self, events, dt):
        self._update_buffer(dt)

        frame_pressed = set()
        frame_released = set()

        for event in events:
            self._handle_event(event, frame_pressed, frame_released)

        axes = self._sample_axes()
        self.raw_axes = axes
        self._update_trigger_action(frame_pressed, frame_released, axes.r_trigger)

        self.frame = InputFrame(
            axes=axes,
            pressed=frozenset(frame_pressed),
            released=frozenset(frame_released),
            held=frozenset(self.held_buttons),
            dt=dt,
        )

        self._enqueue_button_actions(frame_pressed, frame_released)
        self._enqueue_navigation_actions(dt)

    def update_controller(self):
        self.controllers = []
        self.initiate_controls()
        self.get_controller_type()

    def initiate_controls(self):
        for controller_id in range(pygame._sdl2.controller.get_count()):
            self.controllers.append(pygame._sdl2.controller.Controller(controller_id))

    def rumble(self, duration=1000):
        for controller in self.controllers:
            controller.rumble(0, 0.7, duration)

    def get_controller_type(self):
        self.controller_type = ["keyboard"]
        for controller in self.controllers:
            name = controller.name
            if "xbox" in name.lower():
                self.controller_type.append("xbox")
            elif "playstation" in name.lower():
                self.controller_type.append("ps4")
            elif "nintendo" in name.lower():
                self.controller_type.append("nintendo")
            else:
                self.controller_type.append("unknown")

    def is_held(self, button_name):
        return button_name in self.held_buttons

    def get_inputs(self):
        return list(self.input_buffer)

    def clear_buffer(self):
        self.input_buffer.clear()

    def enqueue_action(self, name, pressed=False, released=False, axes=None, lifetime=None):
        if lifetime is None:
            lifetime = self.buffer_lifetime
        self.input_buffer.append(
            InputAction(
                name=name,
                pressed=pressed,
                released=released,
                axes=axes or self.frame.axes,
                lifetime=lifetime,
            )
        )

    def _handle_event(self, event, frame_pressed, frame_released):
        if event.type == pygame.CONTROLLERDEVICEADDED:
            self.update_controller()
            return

        if event.type == pygame.CONTROLLERDEVICEREMOVED:
            self.update_controller()
            return

        if event.type == pygame.KEYDOWN:
            self._handle_keyboard_down(event.key, frame_pressed)
            return

        if event.type == pygame.KEYUP:
            self._handle_keyboard_up(event.key, frame_released)
            return

        if event.type == pygame.CONTROLLERBUTTONDOWN:
            self._handle_controller_down(event.button, frame_pressed)
            return

        if event.type == pygame.CONTROLLERBUTTONUP:
            self._handle_controller_up(event.button, frame_released)

    def _handle_keyboard_down(self, key, frame_pressed):
        action = self.keyboard_buttons.get(key)
        if action and action not in self.held_buttons:
            self.held_buttons.add(action)
            frame_pressed.add(action)
            return

        direction = self.keyboard_directions.get(key)
        if direction:
            self.held_directions.add(direction)

    def _handle_keyboard_up(self, key, frame_released):
        action = self.keyboard_buttons.get(key)
        if action and action in self.held_buttons:
            self.held_buttons.discard(action)
            frame_released.add(action)
            return

        direction = self.keyboard_directions.get(key)
        if direction:
            self.held_directions.discard(direction)

    def _handle_controller_down(self, button, frame_pressed):
        action = self.controller_buttons.get(button)
        if action and action not in self.held_buttons:
            self.held_buttons.add(action)
            frame_pressed.add(action)
            return

        direction = self.controller_directions.get(button)
        if direction:
            self.held_directions.add(direction)

    def _handle_controller_up(self, button, frame_released):
        action = self.controller_buttons.get(button)
        if action and action in self.held_buttons:
            self.held_buttons.discard(action)
            frame_released.add(action)
            return

        direction = self.controller_directions.get(button)
        if direction:
            self.held_directions.discard(direction)

    def _sample_axes(self):
        keys = pygame.key.get_pressed()

        move_x = 0
        move_y = 0
        look_x = 0
        look_y = 0

        if keys[pygame.K_RIGHT]:
            move_x = 1
        if keys[pygame.K_LEFT]:
            move_x = -1
        if keys[pygame.K_UP]:
            move_y = -1
        if keys[pygame.K_DOWN]:
            move_y = 1

        for controller in self.controllers:
            left_x = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTX))
            left_y = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTY))
            right_x = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTX))
            right_y = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTY))
            self.left_trigger_value = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_TRIGGERLEFT))
            self.right_trigger_value = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_TRIGGERRIGHT))

            if abs(left_x) > self.move_deadzone:
                move_x = left_x
            if abs(left_y) > self.move_deadzone:
                move_y = left_y
            if abs(right_x) > self.look_deadzone:
                look_x = right_x
            if abs(right_y) > self.look_deadzone:
                look_y = right_y

        dpad_x = 0
        dpad_y = 0
        if "right" in self.held_directions:
            dpad_x += 1
        if "left" in self.held_directions:
            dpad_x -= 1
        if "down" in self.held_directions:
            dpad_y += 1
        if "up" in self.held_directions:
            dpad_y -= 1

        return AxesSnapshot(
            move=(move_x, move_y),
            look=(look_x, look_y),
            dpad=(dpad_x, dpad_y),
            l_trigger=self.left_trigger_value,
            r_trigger=self.right_trigger_value,
        )

    def _update_trigger_action(self, frame_pressed, frame_released, right_trigger_value):
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
            self.enqueue_action(name=name, pressed=True, axes=self.frame.axes)
        for name in frame_released:
            self.enqueue_action(name=name, released=True, axes=self.frame.axes)

    def _enqueue_navigation_actions(self, dt):
        directions = {
            "up": self.frame.axes.dpad[1] < 0 or self.frame.axes.move[1] < -self.ui_nav_threshold,
            "down": self.frame.axes.dpad[1] > 0 or self.frame.axes.move[1] > self.ui_nav_threshold,
            "left": self.frame.axes.dpad[0] < 0 or self.frame.axes.move[0] < -self.ui_nav_threshold,
            "right": self.frame.axes.dpad[0] > 0 or self.frame.axes.move[0] > self.ui_nav_threshold,
        }

        for direction, active in directions.items():
            state = self.nav_repeat[direction]
            if not active:
                state["active"] = False
                state["timer"] = 0
                continue

            if not state["active"]:
                self.enqueue_action(name=direction, pressed=True, axes=self.frame.axes)
                state["active"] = True
                state["timer"] = self.ui_repeat_delay
                continue

            state["timer"] -= dt
            if state["timer"] <= 0:
                self.enqueue_action(name=direction, pressed=True, axes=self.frame.axes)
                state["timer"] = self.ui_repeat_interval

    def _update_buffer(self, dt):
        retained = deque()
        while self.input_buffer:
            action = self.input_buffer.popleft()
            action.update(dt)
            if not action.is_done:
                retained.append(action)
        self.input_buffer = retained

    @staticmethod
    def normalize_axis(value):
        return value / 32768.0
