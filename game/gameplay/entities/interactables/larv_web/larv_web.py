import pygame

from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.enemies.common.ground.larv.surface_larv import SurfaceLarv
from engine.utils import read_files
from . import states_larv_web 

class LarvWeb(Interactables):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/larv_web/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.currentstate = states_larv_web.Idle(self)

        trigger_distance = kwargs.get('trigger_distance', (90, 110))

        self.anchor_pos = self.rect.center
        self.trigger_distance = list(trigger_distance)
        larv_type = kwargs.get('enemy_type', 'larv')
        larv_cls = self.game_objects.registry.fetch('enemies', larv_type)

        larv_pos = [self.anchor_pos[0], self.anchor_pos[1]]
        self.larv = larv_cls(larv_pos, game_objects, initial_state = 'hanging', anchor_pos = self.anchor_pos)
        self.game_objects.enemies.add(self.larv)

        self.hit_component.set_invincibility(True)          

    def on_collision(self, entity):#one time collision
        pass
        
    def on_noncollision(self, entity):#one time none collision
        pass
