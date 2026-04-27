from gameplay.entities.interactables.base.interactables import Interactables


class BaseArea(Interactables):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.hit_component.set_invincibility(True)

    def update(self, dt):
        pass

    def update_render(self, dt):
        pass

    def on_collision(self, entity):
        pass

    def on_noncollision(self, entity):
        pass

    def release_texture(self):
        pass

    def draw(self, target):
        pass
