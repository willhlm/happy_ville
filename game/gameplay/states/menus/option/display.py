from gameplay.ui.loaders import OptionDisplayLoader
from ..base.base_ui import BaseUI

class OptionDisplay(BaseUI):
    OPTION_KEYS_BY_LABEL = {
        "Resolution": "resolution",
        "Pixel scaling": "pixel_scaling",
        "Vsync": "vsync",
        "Fullscreen": "fullscreen",
        "fps": "fps",
    }

    def __init__(self, game):
        super().__init__(game)
        self.settings = game.settings
        self.menu_ui = OptionDisplay.menu_ui
        self.current_button = 0
        self.previous_button = None
        self._update_arrow()
        self._update_button()

    @staticmethod
    def pool(game_objects):
        OptionDisplay.menu_ui = OptionDisplayLoader(game_objects)

    def _update_arrow(self):
        item = self.menu_ui.navigation_items[self.current_button]
        bx, by, bw, _ = item.rect
        for arrow in self.menu_ui.arrows:
            if arrow.flip:
                x = (
                    self.menu_ui.results[self.current_button][0] + bw + 10
                    if item in self.menu_ui.option_labels
                    else bx + bw + 10
                )
                arrow.set_pos((x, by))
            else:
                arrow.set_pos((bx - arrow.rect.width - 10, by))
        self.play_click_sound()

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
        for label, result_position in zip(
            self.menu_ui.option_labels, self.menu_ui.results
        ):
            label.render(screen)
            self.game.game_objects.font.render(
                screen,
                self.settings.display_option_text(
                    self.OPTION_KEYS_BY_LABEL[label.text]
                ),
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
        label = self.menu_ui.option_labels[self.current_button]
        option_key = self.OPTION_KEYS_BY_LABEL[label.text]
        self.settings.cycle_display_option(option_key, direction)
        self.play_click_sound()

    def _activate_current_item(self):
        item = self.menu_ui.navigation_items[self.current_button]
        if item in self.menu_ui.option_labels:
            self._cycle_current_option(1)
        elif item.text == "Reset to default":
            self.settings.reset_display_options()
            self.game.game_objects.sound.play_ui_sound("select")
        else:
            self.game.game_objects.sound.play_ui_sound("select")
            self.game.state_manager.exit_state()

    def on_pop(self):
        self.settings.save()
        for item in self.menu_ui.navigation_items:
            item.on_exit()

    def play_click_sound(self):
        self.game.game_objects.sound.play_ui_sound("on_select")
