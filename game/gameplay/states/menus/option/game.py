from gameplay.ui.loaders import OptionGameLoader
from ..base.base_ui import BaseUI

class OptionGame(BaseUI):
    """Gameplay preferences which are independent from controller bindings."""

    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = OptionGame.menu_ui
        self.settings = game.settings
        self.options = self.settings.game

        self.current_button = 0
        self.previous_button = None
        self._update_arrow()
        self._update_button()

    @staticmethod
    def pool(game_objects):
        OptionGame.menu_ui = OptionGameLoader(game_objects)

    def _update_arrow(self):
        item = self.menu_ui.navigation_items[self.current_button]
        bx, by, bw, _ = item.rect
        for arrow in self.menu_ui.arrows:
            if arrow.flip:
                arrow.set_pos((bx + bw + 10, by))
            else:
                arrow.set_pos((bx - arrow.rect.width - 10, by))
        self.game.game_objects.sound.play_ui_sound("on_select")

    def _update_button(self):
        if self.previous_button is not None and self.previous_button != self.current_button:
            self.menu_ui.navigation_items[self.previous_button].on_exit()
        if self.previous_button != self.current_button:
            self.menu_ui.navigation_items[self.current_button].on_enter()
        self.previous_button = self.current_button

    def update_render(self, dt):
        self.game.game_objects.ui.menu.update_time(dt)
        self.menu_ui.navigation_items[self.current_button].active()
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)

    def render(self):
        screen = self.game.screen_manager.screen
        screen.clear(0, 0, 0, 0)
        self.game.game_objects.ui.menu.render_background(screen)

        for index, (label, result_position) in enumerate(
            zip(self.menu_ui.option_labels, self.menu_ui.results)
        ):
            label.render(screen)
            self.game.game_objects.font.render(
                screen,
                self._option_text(index),
                letter_frame=None,
                color=[255, 255, 255, 255],
                position=result_position,
            )
        for button in self.menu_ui.menu_buttons:
            button.render(screen)
        for arrow in self.menu_ui.arrows:
            self.game.display.render(
                arrow.image, screen, position=arrow.true_pos, flip=arrow.flip
            )
        self.game.render_display(screen.texture)

    def _option_text(self, index):
        if index == 0:
            return self.options["language"].upper()
        if index == 1:
            return f"{self.options['camera_shake']}%"
        if index == 2:
            return f"{self.options['controller_rumble']}%"
        if index == 3:
            return self.options["hud_appearance"].upper()
        return ""

    def handle_events(self, input):
        input.processed()
        if not input.pressed:
            return
        if input.name == "up":
            self._move_selection(-1)
        elif input.name == "down":
            self._move_selection(1)
        elif input.name == "left":
            self._cycle_current_option(-1)
        elif input.name == "right":
            self._cycle_current_option(1)
        elif input.name in ("start", "b"):
            self.game.state_manager.exit_state()
        elif input.name in ("return", "a"):
            self._activate_current_item()

    def _move_selection(self, direction):
        self.current_button = (self.current_button + direction) % len(
            self.menu_ui.navigation_items
        )
        self._update_arrow()
        self._update_button()

    def _cycle_current_option(self, direction):
        if self.current_button >= len(self.menu_ui.option_labels):
            return
        if self.current_button == 0:
            current = self.settings.LANGUAGE_OPTIONS.index(self.options["language"])
            self.options["language"] = self.settings.LANGUAGE_OPTIONS[
                (current + direction) % len(self.settings.LANGUAGE_OPTIONS)
            ]
        elif self.current_button == 1:
            self._cycle_percentage("camera_shake", direction)
        elif self.current_button == 2:
            self._cycle_percentage("controller_rumble", direction)
        elif self.current_button == 3:
            current = self.settings.HUD_APPEARANCE_OPTIONS.index(
                self.options["hud_appearance"]
            )
            self.options["hud_appearance"] = self.settings.HUD_APPEARANCE_OPTIONS[
                (current + direction) % len(self.settings.HUD_APPEARANCE_OPTIONS)
            ]
        self.game.game_objects.sound.play_ui_sound("on_select")

    def _cycle_percentage(self, setting, direction):
        current = self.settings.EFFECT_PERCENTAGES.index(self.options[setting])
        self.options[setting] = self.settings.EFFECT_PERCENTAGES[
            (current + direction) % len(self.settings.EFFECT_PERCENTAGES)
        ]

    def _activate_current_item(self):
        item = self.menu_ui.navigation_items[self.current_button]
        if item in self.menu_ui.option_labels:
            self._cycle_current_option(1)
        elif item.text == "Reset to default":
            self.settings.reset_game_options()
            self.game.game_objects.sound.play_ui_sound("select")
        else:
            self.game.game_objects.sound.play_ui_sound("select")
            self.game.state_manager.exit_state()

    def on_pop(self):
        self._save_settings()
        for item in self.menu_ui.navigation_items:
            item.on_exit()

    def _save_settings(self):
        self.settings.save()
