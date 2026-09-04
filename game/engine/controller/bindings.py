"""Default mappings and persistent player input bindings."""

import json
from pathlib import Path

import pygame


BUTTON_ACTIONS = frozenset(
    (
        "a",
        "b",
        "x",
        "y",
        "lb",
        "rb",
        "ls",
        "rs",
        "rt",
        "start",
        "select",
        "guide",
        "return",
    )
)
DIRECTION_ACTIONS = frozenset(("up", "down", "left", "right"))
ALL_ACTIONS = BUTTON_ACTIONS | DIRECTION_ACTIONS

DEFAULT_KEYBOARD_BUTTONS = {
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
DEFAULT_KEYBOARD_DIRECTIONS = {
    pygame.K_RIGHT: "right",
    pygame.K_LEFT: "left",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
}
DEFAULT_CONTROLLER_BUTTONS = {
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
DEFAULT_CONTROLLER_DIRECTIONS = {
    pygame.CONTROLLER_BUTTON_DPAD_UP: "up",
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: "down",
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: "left",
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "right",
}


class BindingStore:
    """Own and persist mappings from physical controls to game actions."""

    VERSION = 1

    def __init__(self, path="config/input_bindings.json"):
        self.path = Path(path)
        self.reset(save=False)
        self.load()

    def reset(self, save=True):
        self.keyboard_buttons = dict(DEFAULT_KEYBOARD_BUTTONS)
        self.keyboard_directions = dict(DEFAULT_KEYBOARD_DIRECTIONS)
        self.controller_buttons = dict(DEFAULT_CONTROLLER_BUTTONS)
        self.controller_directions = dict(DEFAULT_CONTROLLER_DIRECTIONS)
        if save:
            self.save()

    def data(self):
        return {
            "version": self.VERSION,
            "keyboard": self._serialise(
                self.keyboard_buttons, self.keyboard_directions
            ),
            "controller": self._serialise(
                self.controller_buttons, self.controller_directions
            ),
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as binding_file:
            json.dump(self.data(), binding_file, indent=2, sort_keys=True)
            binding_file.write("\n")
        temporary_path.replace(self.path)

    def load(self):
        try:
            with self.path.open(encoding="utf-8") as binding_file:
                data = json.load(binding_file)
        except (OSError, json.JSONDecodeError):
            return False
        if not isinstance(data, dict) or data.get("version") != self.VERSION:
            return False
        self._load_device(
            data.get("keyboard"), self.keyboard_buttons, self.keyboard_directions
        )
        self._load_device(
            data.get("controller"), self.controller_buttons, self.controller_directions
        )
        return True

    def rebind(self, device, action, input_id):
        if action not in ALL_ACTIONS:
            raise ValueError(f"Unknown input action: {action}")
        if not isinstance(input_id, int):
            raise TypeError("Input identifiers must be pygame integer constants")
        buttons, directions = self.device_maps(device)
        buttons.pop(input_id, None)
        directions.pop(input_id, None)
        target = directions if action in DIRECTION_ACTIONS else buttons
        for bound_input, bound_action in tuple(target.items()):
            if bound_action == action:
                del target[bound_input]
        target[input_id] = action
        self.save()

    def binding_name(self, device, action):
        buttons, directions = self.device_maps(device)
        for input_id, bound_action in {**buttons, **directions}.items():
            if bound_action == action:
                return (
                    pygame.key.name(input_id) if device == "keyboard" else str(input_id)
                )
        return None

    def device_maps(self, device):
        if device == "keyboard":
            return self.keyboard_buttons, self.keyboard_directions
        if device == "controller":
            return self.controller_buttons, self.controller_directions
        raise ValueError(f"Unknown input device: {device}")

    @staticmethod
    def _serialise(buttons, directions):
        return {
            "buttons": [[input_id, action] for input_id, action in buttons.items()],
            "directions": [
                [input_id, action] for input_id, action in directions.items()
            ],
        }

    def _load_device(self, data, buttons, directions):
        if not isinstance(data, dict):
            return
        loaded_buttons = self._parse(data.get("buttons"), BUTTON_ACTIONS)
        loaded_directions = self._parse(data.get("directions"), DIRECTION_ACTIONS)
        if loaded_buttons is not None:
            buttons.clear()
            buttons.update(loaded_buttons)
        if loaded_directions is not None:
            directions.clear()
            directions.update(loaded_directions)

    @staticmethod
    def _parse(entries, valid_actions):
        if not isinstance(entries, list):
            return None
        bindings = {}
        for entry in entries:
            if (
                not isinstance(entry, list)
                or len(entry) != 2
                or not isinstance(entry[0], int)
                or entry[1] not in valid_actions
            ):
                return None
            bindings[entry[0]] = entry[1]
        return bindings
