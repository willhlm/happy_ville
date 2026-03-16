from gameplay.entities.interactables import TwoDLiquid
from gameplay.narrative.quests_events.base import Tasks


class AcidEscape(Tasks):#called in golden fields "last room"
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        pos = [-2000 + game_objects.camera_manager.camera.scroll[0],game_objects.game.window_size[1] + game_objects.camera_manager.camera.scroll[1]]
        size = [5000, game_objects.game.window_size[1]]
        self.acid = TwoDLiquid(pos, game_objects, size, 'bg1', vertical = True)
        game_objects.interactables_fg.add(self.acid)

    def complete(self):
        self.game_objects.world_state.narrative.update_event(type(self).__name__.lower())
        self.acid.kill()
