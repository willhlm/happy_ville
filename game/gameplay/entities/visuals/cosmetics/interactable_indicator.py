import math 
from gameplay.entities.base.static_entity import StaticEntity
from engine.utils import read_files

class InteractableIndicator(StaticEntity):#the hoovering above things to indicat it is interactable, or only for NPC?
    def __init__(self, pos, game_objects, size = (32,32)):
        super().__init__(pos, game_objects)
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        InteractableIndicator.sprites = read_files.load_sprites_dict("assets/sprites/entities/visuals/cosmetics/text_bubble/", game_objects)

    def release_texture(self):
        pass

    def update(self, dt):
        self.update_vel(dt)
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0] * dt, self.true_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos

    def update_vel(self, dt):
        self.time += dt * 0.1
        self.velocity[1] = 0.25*math.sin(self.time)

    def draw(self, target):
        blit_pos = [
            int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]),
            int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1]),
        ]
        self.game_objects.game.display.render(self.sprites['small'][0], target, position=blit_pos)

