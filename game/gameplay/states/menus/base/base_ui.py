from gameplay.states.base.game_state import GameState

class BaseUI(GameState):
    def __init__(self, game, **kwarg):
        super().__init__(game)
 