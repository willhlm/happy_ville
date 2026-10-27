from gameplay.states.gameplay.gameplay import Gameplay
from gameplay.ui.components import MenuBox


class ConfirmationDialog(Gameplay):
    """Small reusable yes/no prompt rendered over the active world."""

    def __init__(self, game, text, on_confirm=None, on_cancel=None):
        super().__init__(game)
        self.text = text
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.actions = ('yes', 'no')
        self.index = 0
        self.pointer = MenuBox(self.game.game_objects)
        self.overlay = self.game.display.make_layer(self.game.window_size)

    def on_pop(self):
        self.overlay.release()

    def handle_movement(self):
        pass

    def render(self):
        super().render()

        width, height = self.game.window_size
        box_size = (240, 80)
        box_pos = (
            int(width * 0.5 - box_size[0] * 0.5),
            int(height * 0.25),
        )
        action_y = box_pos[1] + 48
        action_positions = (
            (box_pos[0] + 76, action_y),
            (box_pos[0] + 146, action_y),
        )

        self.overlay.clear(0, 0, 0, 0)
        self.game.game_objects.font.render_text_bg(
            self.overlay,
            box_size,
            position=box_pos,
        )
        self.game.game_objects.font.render(
            self.overlay,
            self.text,
            position=(box_pos[0] + 12, box_pos[1] + 12),
            width=box_size[0] - 24,
        )
        for action, position in zip(self.actions, action_positions):
            self.game.game_objects.font.render(
                self.overlay,
                action,
                position=position,
            )
        self.game.display.render(
            self.pointer.image,
            self.overlay,
            position=action_positions[self.index],
        )
        self.game.display.render(
            self.overlay.texture,
            self.game.screen_manager.composite_screen,
        )
        self.game.render_display(
            self.game.screen_manager.composite_screen.texture,
            scale=False,
        )

    def handle_events(self, input):
        input.processed()
        if not input.pressed:
            return

        if input.name == 'left':
            self.index = 0
        elif input.name == 'right':
            self.index = 1
        elif input.name in ('start', 'select', 'b'):
            self._finish(self.on_cancel)
        elif input.name in ('a', 'return'):
            callback = self.on_confirm if self.index == 0 else self.on_cancel
            self._finish(callback)

    def _finish(self, callback):
        self.game.state_manager.exit_state()
        if callback:
            callback()
