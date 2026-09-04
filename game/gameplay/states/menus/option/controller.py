from gameplay.ui.loaders import ControllerMenuLoader
from ..base.base_ui import BaseUI


class ControllerMenu(BaseUI):
    """Controller-options screen for rebinding the core gameplay actions."""

    ACTIONS = ("a", "x", "lb", "select", "rb")

    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = ControllerMenu.menu_ui
        self.current_button = 0
        self.previous_button = None
        self.waiting_for_binding = False
        self._update_arrow()
        self._update_button()

    @staticmethod
    def pool(game_objects):
        ControllerMenu.menu_ui = ControllerMenuLoader(game_objects)

    def _update_arrow(self):
        button = self.menu_ui.option_labels[self.current_button]
        bx, by, bw, bh = button.rect
        for index, arrow in enumerate(self.menu_ui.arrows):
            result_x = self.menu_ui.results[index][0]
            if arrow.flip:
                arrow.set_pos((result_x + bw + 10, by))
            else:
                arrow.set_pos((bx - arrow.rect.width - 10, by))
        self.game.game_objects.sound.play_ui_sound("on_select")

    def update_render(self, dt):
        self.game.game_objects.ui.menu.update_time(dt)
        self.menu_ui.option_labels[self.current_button].active()
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)

    def render(self):
        self.game.screen_manager.screen.clear(0, 0, 0, 0)
        self.game.game_objects.ui.menu.render_background(
            self.game.screen_manager.screen
        )
        for index, label in enumerate(self.menu_ui.option_labels):
            label.render(self.game.screen_manager.screen)
            value = (
                "PRESS A KEY..."
                if self.waiting_for_binding and index == self.current_button
                else self._binding_text(index)
            )
            self.game.game_objects.font.render(
                self.game.screen_manager.screen,
                value,
                letter_frame=None,
                color=[255, 255, 255, 255],
                position=self.menu_ui.results[index],
            )
        for arrow in self.menu_ui.arrows:
            self.game.display.render(
                arrow.image,
                self.game.screen_manager.screen,
                position=arrow.true_pos,
                flip=arrow.flip,
            )
        self.game.render_display(self.game.screen_manager.screen.texture)

    def _update_button(self):
        if (
            self.previous_button is not None
            and self.previous_button != self.current_button
        ):
            self.menu_ui.option_labels[self.previous_button].on_exit()
        if self.previous_button != self.current_button:
            self.menu_ui.option_labels[self.current_button].on_enter()
        self.previous_button = self.current_button

    def handle_events(self, input):
        input.processed()
        if input.name == "binding_captured":
            self.waiting_for_binding = False
            self.game.game_objects.sound.play_ui_sound("select")
            return
        if self.waiting_for_binding or not input.pressed:
            return
        if input.name == "up":
            self.current_button = (self.current_button - 1) % len(
                self.menu_ui.option_labels
            )
            self._update_arrow()
            self._update_button()
        elif input.name == "down":
            self.current_button = (self.current_button + 1) % len(
                self.menu_ui.option_labels
            )
            self._update_arrow()
            self._update_button()
        elif input.name == "start":
            self.game.state_manager.exit_state()
        elif input.name in ("return", "a"):
            self.game.game_objects.sound.play_ui_sound("select")
            self.begin_rebind()

    def begin_rebind(self):
        self.waiting_for_binding = True
        self.game.game_objects.controller.begin_rebind(
            self.ACTIONS[self.current_button]
        )

    def _binding_text(self, index):
        controller = self.game.game_objects.controller
        device = "keyboard" if controller.prompt_type == "keyboard" else "controller"
        return (
            controller.binding_name(device, self.ACTIONS[index]) or "UNBOUND"
        ).upper()

    def on_exit(self):
        self.game.game_objects.controller.cancel_rebind()
        for label in self.menu_ui.option_labels:
            label.on_exit()
