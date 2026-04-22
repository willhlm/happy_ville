from gameplay.states import Gameplay

class BackpackUIState(Gameplay):#pressing i: map, inventory, omamori, journal
    def __init__(self, game, page, **kwarg):
        super().__init__(game)
        self.game.game_objects.ui.backpack.open_page(page, **kwarg)

    def on_pop(self):
        self.game.game_objects.ui.backpack.close_page()

    def update(self, dt):
        super().update(dt)
        self.game.game_objects.ui.backpack.update(dt)

    def render(self):
        super().render()
        self.game.game_objects.ui.backpack.render()

    def handle_events(self,input):
        self.game.game_objects.ui.backpack.handle_events(input)

    def handle_movement(self):#so aila doesn't move
        pass
