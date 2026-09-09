from gameplay.ui.loaders import OptionControllerLoader
from gameplay.ui.managers.backpack_pages.navigation import find_closest_in_direction
from ..base.base_ui import BaseUI


class OptionController(BaseUI):
    """Controller-options screen for rebinding the core gameplay actions."""

    ACTIONS_BY_LABEL = {
        "Jump": "jump",
        "Attack": "attack",
        "Interact": "interact",
        "Ability": "ability",
        "Dash": "dash",
        "Ability wheel": "ability_select",
        "Inventory": "inventory",
    }

    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = OptionController.menu_ui
        self.current_button = 0
        self.previous_button = None
        self.waiting_for_binding = False
        self._update_arrow()
        self._update_button()

    @staticmethod
    def pool(game_objects):
        OptionController.menu_ui = OptionControllerLoader(game_objects)

    def _update_arrow(self):
        button = self.menu_ui.navigation_items[self.current_button]
        bx, by, bw, bh = button.rect
        for arrow in self.menu_ui.arrows:
            if arrow.flip:
                arrow.set_pos((bx + bw + 10, by))
            else:
                arrow.set_pos((bx - arrow.rect.width - 10, by))
        self.game.game_objects.sound.play_ui_sound("on_select")

    def update_render(self, dt):
        self.game.game_objects.ui.menu.update_time(dt)
        self.menu_ui.navigation_items[self.current_button].active()
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)

    def render(self):
        self.game.screen_manager.screen.clear(0, 0, 0, 0)
        self.game.game_objects.ui.menu.render_background(
            self.game.screen_manager.screen
        )
        for label, result_position in zip(
            self.menu_ui.option_labels, self.menu_ui.results
        ):
            label.render(self.game.screen_manager.screen)
            value = (
                "PRESS A KEY..."
                if self.waiting_for_binding
                and self.menu_ui.navigation_items[self.current_button] is label
                else self._binding_text(label)
            )
            self.game.game_objects.font.render(
                self.game.screen_manager.screen,
                value,
                letter_frame=None,
                color=[255, 255, 255, 255],
                position=result_position,
            )
        for button in self.menu_ui.menu_buttons:
            button.render(self.game.screen_manager.screen)
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
            self.menu_ui.navigation_items[self.previous_button].on_exit()
        if self.previous_button != self.current_button:
            self.menu_ui.navigation_items[self.current_button].on_enter()
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
            self.move_selection("up")
        elif input.name == "down":
            self.move_selection("down")
        elif input.name == "left":
            self.move_selection("left")
        elif input.name == "right":
            self.move_selection("right")
        elif input.name == "start":
            self.game.state_manager.exit_state()
        elif input.name in ("return", "a"):
            self.game.game_objects.sound.play_ui_sound("select")
            self.activate_current_item()

    def move_selection(self, direction):
        items = self.menu_ui.navigation_items
        target = find_closest_in_direction(items[self.current_button], items, direction)
        if target is None:
            return
        self.current_button = items.index(target)
        self._update_arrow()
        self._update_button()

    def activate_current_item(self):
        item = self.menu_ui.navigation_items[self.current_button]
        if item in self.menu_ui.option_labels:
            self.begin_rebind(item)
        elif item.text == "Reset to default":
            self.game.game_objects.input_manager.reset_context("gameplay")
        else:
            self.game.state_manager.exit_state()

    def begin_rebind(self, label):
        self.waiting_for_binding = True
        self.game.game_objects.input_manager.begin_rebind(
            "gameplay", self.ACTIONS_BY_LABEL[label.text]
        )

    def _binding_text(self, label):
        controller = self.game.game_objects.controller
        device = "keyboard" if controller.prompt_type == "keyboard" else "controller"
        binding = self.game.game_objects.input_manager.binding_name(
            "gameplay", self.ACTIONS_BY_LABEL[label.text], device
        )
        return (binding or "UNBOUND").upper()

    def on_exit(self):
        self._cleanup()

    def on_pop(self):
        self._cleanup()

    def _cleanup(self):
        self.game.game_objects.input_manager.cancel_rebind()
        for item in self.menu_ui.navigation_items:
            item.on_exit()
