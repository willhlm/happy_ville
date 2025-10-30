from gameplay.entities.interactables.base.interactables import Interactables

class PlaceHolderInteracatble(Interactables):
    def __init__(self,entity, game_objects):
        super().__init__(entity.rect.center, game_objects)
        self.entity = entity
        self.hitbox = entity.hitbox

    def update(self, dt):
        pass

    def draw(self, target):
        pass

    def interact(self):#when player press T
        self.entity.interact()

    def release_texture(self):
        pass