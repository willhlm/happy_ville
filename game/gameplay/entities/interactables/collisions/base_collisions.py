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

    def take_hit(self, effect):
        """Delegate to hit component"""      
        effect.attacker_callbacks = {}
        effect.attacker_callbacks = {}
        return self.hit_component.take_hit(effect)        