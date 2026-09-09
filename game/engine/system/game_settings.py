from engine.utils import read_files


class GameSettings:
    """Persistent settings shared by the game's option pages and systems."""

    PATH = "config/game_settings.json"
    LANGUAGE_OPTIONS = ("English",)
    HUD_APPEARANCE_OPTIONS = ("on", "auto")
    EFFECT_PERCENTAGES = (100, 75, 50, 25, 0)
    RESOLUTION_OPTIONS = ((640, 360), (800, 450))
    FPS_OPTIONS = (30, 60, 120)
    PIXEL_SCALING_OPTIONS = ("pixel_perfect", "smooth_fit")
    VOLUME_OPTIONS = tuple(range(11))
    GAME_DEFAULTS = {
        "language": "English",
        "camera_shake": 100,
        "controller_rumble": 100,
        "hud_appearance": "auto",
    }
    DISPLAY_DEFAULTS = {
        "vsync": True,
        "fullscreen": False,
        "resolution": list(RESOLUTION_OPTIONS[0]),
        "fps": FPS_OPTIONS[1],
        "pixel_scaling": PIXEL_SCALING_OPTIONS[0],
    }
    SOUND_DEFAULTS = {"overall": 10, "SFX": 10, "music": 10}

    def __init__(self):
        self.data = read_files.read_json(self.PATH)
        self.game = self.data.setdefault("game", {})
        self.display = self.data.setdefault("display", {})
        self.sounds = self.data.setdefault("sounds", {})
        for key, value in self.GAME_DEFAULTS.items():
            self.game.setdefault(key, value)
        for key, value in self.DISPLAY_DEFAULTS.items():
            self.display.setdefault(key, value)
        for key, value in self.SOUND_DEFAULTS.items():
            self.sounds.setdefault(key, value)
        self.game["camera_shake"] = self._normalise_percentage(
            self.game["camera_shake"]
        )
        self.game["controller_rumble"] = self._normalise_percentage(
            self.game["controller_rumble"]
        )
        self.game["language"] = self._normalise_choice(
            self.game["language"], self.LANGUAGE_OPTIONS
        )
        self.game["hud_appearance"] = self._normalise_choice(
            self.game["hud_appearance"], self.HUD_APPEARANCE_OPTIONS
        )
        self.display["resolution"] = list(
            self._normalise_choice(
                tuple(self.display["resolution"]), self.RESOLUTION_OPTIONS
            )
        )
        self.display["fps"] = self._normalise_choice(
            self.display["fps"], self.FPS_OPTIONS
        )
        self.display["pixel_scaling"] = self._normalise_choice(
            self.display["pixel_scaling"], self.PIXEL_SCALING_OPTIONS
        )
        for key, value in self.sounds.items():
            self.sounds[key] = self._normalise_choice(value, self.VOLUME_OPTIONS)

    @classmethod
    def _normalise_percentage(cls, value):
        if isinstance(value, bool):
            return 100 if value else 0
        try:
            value = int(value)
        except (TypeError, ValueError):
            return 100
        return min(cls.EFFECT_PERCENTAGES, key=lambda choice: abs(choice - value))

    @staticmethod
    def _normalise_choice(value, choices):
        return value if value in choices else choices[0]

    @property
    def language(self):
        return self.game["language"]

    @property
    def camera_shake(self):
        return self.game["camera_shake"]

    @property
    def controller_rumble(self):
        return self.game["controller_rumble"]

    @property
    def hud_appearance(self):
        return self.game["hud_appearance"]

    @property
    def pixel_scaling(self):
        return self.display["pixel_scaling"]

    def reset_game_options(self):
        self.game.update(self.GAME_DEFAULTS)

    def reset_display_options(self):
        self.display.update(self.DISPLAY_DEFAULTS)

    def display_option_text(self, key):
        value = self.display[key]
        if key == "resolution":
            return f"{value[0]}x{value[1]}"
        if key == "pixel_scaling":
            return "PIXEL PERFECT" if value == "pixel_perfect" else "SMOOTH FIT"
        if key in ("vsync", "fullscreen"):
            return "ON" if value else "OFF"
        return str(value)

    def cycle_display_option(self, key, direction):
        if key == "resolution":
            self.display[key] = list(
                self._cycle_choice(
                    tuple(self.display[key]), self.RESOLUTION_OPTIONS, direction
                )
            )
        elif key == "pixel_scaling":
            self.display[key] = self._cycle_choice(
                self.display[key], self.PIXEL_SCALING_OPTIONS, direction
            )
        elif key in ("vsync", "fullscreen"):
            self.display[key] = not self.display[key]
        elif key == "fps":
            self.display[key] = self._cycle_choice(
                self.display[key], self.FPS_OPTIONS, direction
            )

    @staticmethod
    def _cycle_choice(value, choices, direction):
        return choices[(choices.index(value) + direction) % len(choices)]

    def reset_sound_options(self):
        self.sounds.update(self.SOUND_DEFAULTS)

    def save(self):
        read_files.write_json(self.data, self.PATH)
