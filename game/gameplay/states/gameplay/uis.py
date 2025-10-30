from gameplay.states import Gameplay

class UIs(Gameplay):#pressing i: map, inventory, omamori, journal
    def __init__(self, game, page, **kwarg):
        super().__init__(game)
        self.game.game_objects.ui.set_ui(page, **kwarg)

    def update(self, dt):
        super().update(dt)
        self.game.game_objects.ui.update(dt)

    def render(self):
        super().render()
        self.game.game_objects.ui.render()

    def handle_events(self,input):
        self.game.game_objects.ui.handle_events(input)

