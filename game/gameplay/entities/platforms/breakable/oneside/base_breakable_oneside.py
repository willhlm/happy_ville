from gameplay.entities.platforms.breakable.base_breakable import BaseBreakable

class BaseBreakableOneside(BaseBreakable):
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.ID_key = ID

    def kill(self):#called when death animatin finishes
        super().kill()
        self.game_objects.world_state.state[self.game_objects.map.level_name]['breakable_platform'][self.ID_key] = True#write in the
