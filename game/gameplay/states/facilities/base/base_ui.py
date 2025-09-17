from gameplay.states import Gameplay

class BaseUI(Gameplay):
    def __init__(self, game, **kwarg):
        super().__init__(game)
        self.screen_alpha = kwarg.get('screen_alpha', 0)
        self.letter_frame = 0#for descriptions

    def update(self):
        super().update()#do we want the BG to be updating while interacting

    def render(self):
        super().render()

    def handle_events(self,input):
        input.processed()   