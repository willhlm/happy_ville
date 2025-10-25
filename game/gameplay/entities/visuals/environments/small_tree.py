import pygame, random
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects

class SmallTree_1(LayeredObjects):
    animations = {}
    def __init__(self, pos, game_objects,parallax,layer_name, live_blur = False):
        super().__init__(pos, game_objects,parallax,layer_name, live_blur)
        self.init_sprites('assets/sprites/entities/visuals/environments/trees/nordveden/small_tree_1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.time = 0

        self.shader = game_objects.shaders['sway_wind']
        self.offset = random.uniform(0,10)

    def update(self):
        self.time += self.game_objects.game.dt
        self.group_distance()

    def draw(self,target):
        self.shader['TIME'] = self.time
        self.shader['offset'] = self.offset
        self.shader['upsidedown'] = 0
        super().draw(target)