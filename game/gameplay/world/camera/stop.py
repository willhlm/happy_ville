from gameplay.entities.base.static_entity import StaticEntity
from gameplay.world.camera import states

class Stop(StaticEntity):
    def __init__(self, game_objects, size, pos, dir, offset):
        super().__init__(pos, game_objects)
        self.hitbox = self.rect.inflate(0,0)
        self.size = size
        self.rect[2], self.rect[3] = size[0], size[1]
        self.offset = int(offset)#number of tiles in the "negative direction" in which the stop should apply
        self.currentstate = getattr(states, 'Idle_' + dir)(self)

    def release_texture(self):#called when .kill() and empty group
        pass

    def update(self, dt):
        self.currentstate.update(dt)