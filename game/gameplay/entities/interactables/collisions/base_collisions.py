from gameplay.entities.interactables.base.interactables import Interactables

class BaseCollisions(Interactables):#with sprites
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.hit_component.set_invinsibility(True)

    def update(self, dt):      
        self.group_distance()

    def update_render(self, dt):      
        pass

    def on_collision(self, entity):#one time collision
        pass

    def on_noncollision(self, entity):#one time none collision
        pass

    def release_texture(self):
        pass

    def draw(self, target):
        pass