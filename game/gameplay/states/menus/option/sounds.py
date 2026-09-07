from gameplay.ui.loaders import OptionSoundsLoader

from ..base.base_ui import BaseUI


class OptionSounds(BaseUI):
    SOUND_KEYS = ("overall", "SFX", "music")

    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = OptionSounds.menu_ui
        self.settings = game.settings
        self.current_button = 0
        self.previous_button = None
        self._update_arrow()
        self._update_button()

    @staticmethod
    def pool(game_objects):
        OptionSounds.menu_ui = OptionSoundsLoader(game_objects)

    def _update_arrow(self):
        item = self.menu_ui.navigation_items[self.current_button]
        bx, by, bw, _ = item.rect
        for arrow in self.menu_ui.arrows:
            if arrow.flip:
                x = (
                    self.menu_ui.results[self.current_button][0] + 20
                    if item in self.menu_ui.option_labels
                    else bx + bw + 10
                )
                arrow.set_pos((x, by))
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
        self._update_sliders()

    def _update_sliders(self):
        volumes = self.game.game_objects.sound.volume_settings
        for key, slider in zip(self.SOUND_KEYS, self.menu_ui.slider):
            slider.set_volume(volumes[key])

    def render(self):
        screen = self.game.screen_manager.screen
        screen.clear(0, 0, 0, 0)
        self.game.game_objects.ui.menu.render_background(screen)
        volumes = self.game.game_objects.sound.volume_settings
        for key, label, result_position in zip(
            self.SOUND_KEYS, self.menu_ui.option_labels, self.menu_ui.results
        ):
            label.render(screen)
            self.game.game_objects.font.render(
                screen,
                str(volumes[key]),
                letter_frame=None,
                color=[255, 255, 255, 255],
                position=result_position,
            )
        for slider in self.menu_ui.slider:
            slider.render(screen)
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
        elif input.name == "right":
            self._change_volume(1)
        elif input.name == "left":
            self._change_volume(-1)
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

    def _change_volume(self, direction):
        if self.current_button >= len(self.menu_ui.option_labels):
            return
        key = self.SOUND_KEYS[self.current_button]
        sound = self.game.game_objects.sound
        sound.change_volume(key, direction)
        sound.update_all_volumes()
        sound.play_ui_sound("on_select")

    def _activate_current_item(self):
        item = self.menu_ui.navigation_items[self.current_button]
        if item in self.menu_ui.option_labels:
            self._change_volume(1)
        elif item.text == "Reset to default":
            self.settings.reset_sound_options()
            default_volumes = dict(self.settings.sounds)
            self.game.game_objects.sound.replace_volume_settings(default_volumes)
            self.game.game_objects.sound.play_ui_sound("select")
        else:
            self.game.game_objects.sound.play_ui_sound("select")
            self.game.state_manager.exit_state()

    def on_pop(self):
        self.settings.sounds.clear()
        self.settings.sounds.update(
            self.game.game_objects.sound.volume_settings
        )
        self.settings.save()
        for item in self.menu_ui.navigation_items:
            item.on_exit()
