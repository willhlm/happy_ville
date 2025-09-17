import pygame, random
from gameplay.entities.visuals.enviroment.base.layered_objects import LayeredObjects

class Vines_1(LayeredObjects):#light forest
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name,live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name,live_blur)
        self.init_sprites('assets/sprites/animations/vines/vines_1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.true_pos = self.rect.topleft
        self.shader = game_objects.shaders['sway_wind']
        self.time = 0
        self.offset = random.uniform(0,10)
        self.upsidedown = 1

    def update(self):
        self.time += self.game_objects.game.dt
        self.group_distance()

    def draw(self,target):
        self.shader['TIME'] = self.time
        self.shader['offset'] = self.offset
        self.shader['upsidedown'] = self.upsidedown
        super().draw(target)