"""Context-specific mappings from controller input tokens to game input tokens."""

import json
from pathlib import Path

import pygame


# These are deliberately the current game tokens. States can be migrated to
# more descriptive names later without changing the context/rebinding design.
GAMEPLAY_DEFAULTS = {
    f"keyboard:{pygame.K_ESCAPE}": "pause",
    f"keyboard:{pygame.K_TAB}": "ability_select",
    f"keyboard:{pygame.K_SPACE}": "jump",
    f"keyboard:{pygame.K_t}": "interact",
    f"keyboard:{pygame.K_e}": "ability",
    f"keyboard:{pygame.K_f}": "attack",
    f"keyboard:{pygame.K_i}": "inventory",
    f"keyboard:{pygame.K_LSHIFT}": "dash",
    f"controller:{pygame.CONTROLLER_BUTTON_A}": "jump",
    f"controller:{pygame.CONTROLLER_BUTTON_B}": "ability",
    f"controller:{pygame.CONTROLLER_BUTTON_X}": "attack",
    f"controller:{pygame.CONTROLLER_BUTTON_Y}": "interact",
    f"controller:{pygame.CONTROLLER_BUTTON_START}": "pause",
    f"controller:{pygame.CONTROLLER_BUTTON_BACK}": "inventory",
    f"controller:{pygame.CONTROLLER_BUTTON_LEFTSHOULDER}": "dash",
    f"controller:{pygame.CONTROLLER_BUTTON_RIGHTSHOULDER}": "ability_select",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "rt": "heal",
    "return": "return",
}
GAMEPLAY_ACTIONS = frozenset(GAMEPLAY_DEFAULTS.values())

UI_DEFAULTS = {
    f"keyboard:{pygame.K_ESCAPE}": "start",
    f"keyboard:{pygame.K_TAB}": "rb",
    f"keyboard:{pygame.K_SPACE}": "a",
    f"keyboard:{pygame.K_t}": "y",
    f"keyboard:{pygame.K_e}": "b",
    f"keyboard:{pygame.K_f}": "x",
    f"keyboard:{pygame.K_g}": "y",
    f"keyboard:{pygame.K_i}": "select",
    f"keyboard:{pygame.K_LSHIFT}": "lb",
    f"keyboard:{pygame.K_RETURN}": "return",
    f"controller:{pygame.CONTROLLER_BUTTON_A}": "a",
    f"controller:{pygame.CONTROLLER_BUTTON_B}": "b",
    f"controller:{pygame.CONTROLLER_BUTTON_X}": "x",
    f"controller:{pygame.CONTROLLER_BUTTON_Y}": "y",
    f"controller:{pygame.CONTROLLER_BUTTON_START}": "start",
    f"controller:{pygame.CONTROLLER_BUTTON_BACK}": "select",
    f"controller:{pygame.CONTROLLER_BUTTON_LEFTSHOULDER}": "lb",
    f"controller:{pygame.CONTROLLER_BUTTON_RIGHTSHOULDER}": "rb",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}


class InputManager:
    """Apply the active state's input context to raw controller actions."""

    VERSION = 1
    GAMEPLAY_CONTEXT = "gameplay"
    UI_CONTEXT = "ui"
    GAMEPLAY_STATES = frozenset(("gameplay", "ability_select"))

    def __init__(self, controller, mappings_path="config/input_mappings.json"):
        self.controller = controller
        self.mappings_path = Path(mappings_path)
        self.context_maps = {
            self.GAMEPLAY_CONTEXT: dict(GAMEPLAY_DEFAULTS),
            self.UI_CONTEXT: dict(UI_DEFAULTS),
        }
        self.pending_rebind = None
        if not self.load():
            self.save()

    def context_for_state(self, state_name):
        if state_name in self.GAMEPLAY_STATES:
            return self.GAMEPLAY_CONTEXT
        return self.UI_CONTEXT

    def get_inputs(self, state_name):
        context = self.context_for_state(state_name)
        translated = []
        for input_action in self.controller.get_inputs():
            if input_action.is_done:
                continue
            if input_action.name == "binding_captured":
                self._complete_capture(input_action)
                translated.append(input_action)
                continue
            if self._translate(input_action, context):
                translated.append(input_action)
        return translated

    def begin_rebind(self, context, action):
        if context != self.GAMEPLAY_CONTEXT or action not in GAMEPLAY_ACTIONS:
            raise ValueError(f"{action!r} is not bindable in the {context!r} context")
        self.pending_rebind = (context, action)
        self.controller.begin_capture()

    def cancel_rebind(self):
        self.pending_rebind = None
        self.controller.cancel_capture()

    def rebind(self, context, action, source_action):
        mappings = self.context_maps[context]
        for source, mapped_action in tuple(mappings.items()):
            if mapped_action == action or source == source_action:
                del mappings[source]
        mappings[source_action] = action
        self.save()

    def reset_context(self, context):
        if context != self.GAMEPLAY_CONTEXT:
            raise ValueError(f"No reset defaults are defined for {context!r}")
        self.context_maps[context] = dict(GAMEPLAY_DEFAULTS)
        self.save()

    def is_held(self, context, action):
        """Return whether the physical control bound to an action is held."""
        mappings = self.context_maps.get(context, {})
        return any(
            self.controller.is_control_held(source)
            for source, mapped_action in mappings.items()
            if mapped_action == action
        )

    def binding_name(self, context, action, device):
        """Return the device-specific label for a contextual action binding."""
        mappings = self.context_maps.get(context, {})
        for source, mapped_action in mappings.items():
            if mapped_action == action:
                label = self._display_control(source, device)
                if label is not None:
                    return label
        return None

    def save(self):
        self.mappings_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.mappings_path.with_suffix(
            self.mappings_path.suffix + ".tmp"
        )
        with temporary_path.open("w", encoding="utf-8") as mapping_file:
            json.dump(
                {"version": self.VERSION, "contexts": self.context_maps},
                mapping_file,
                indent=2,
                sort_keys=True,
            )
            mapping_file.write("\n")
        temporary_path.replace(self.mappings_path)

    def load(self):
        try:
            with self.mappings_path.open(encoding="utf-8") as mapping_file:
                data = json.load(mapping_file)
        except (OSError, json.JSONDecodeError):
            return False
        contexts = data.get("contexts") if isinstance(data, dict) else None
        gameplay = (
            contexts.get(self.GAMEPLAY_CONTEXT) if isinstance(contexts, dict) else None
        )
        if (
            not isinstance(data, dict)
            or data.get("version") != self.VERSION
            or not self._valid_gameplay_map(gameplay)
        ):
            return False
        self.context_maps[self.GAMEPLAY_CONTEXT] = gameplay
        return True

    def _translate(self, input_action, context):
        raw_action = input_action.meta.get("raw_action", input_action.name)
        input_action.meta["raw_action"] = raw_action
        source = input_action.meta.get("physical_input") or raw_action
        mapped_action = self.context_maps[context].get(source)
        if mapped_action is None:
            input_action.processed()
            return False
        input_action.name = mapped_action
        return True

    def _complete_capture(self, input_action):
        if self.pending_rebind is None:
            return
        context, action = self.pending_rebind
        source = input_action.meta.get("source_action")
        self.rebind(context, action, source)
        self.pending_rebind = None

    @staticmethod
    def _valid_gameplay_map(mappings):
        return (
            isinstance(mappings, dict)
            and bool(mappings)
            and all(isinstance(source, str) for source in mappings)
            and set(mappings.values()).issubset(GAMEPLAY_ACTIONS)
        )

    @staticmethod
    def _display_control(source, device):
        try:
            kind, value = source.split(":", 1)
            value = int(value)
        except ValueError:
            return None
        if kind == "keyboard":
            return pygame.key.name(value)
        if kind == "controller" and device == "controller":
            return f"BUTTON {value}"
        return None
