import pygame
from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform
from . import states_smacker

class Smacker(DynamicPlatform):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/traps/smacker/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.true_pos = list(self.rect.topleft)
        self.old_hitbox = self.hitbox.copy()

        self.hole = kwarg.get('hole', None)

        self.frequency = int(kwarg.get('frequency', 100))#infinte -> idle - active
        self.distance = kwarg.get('distance', 4*16)
        self.original_pos = pos

        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.currentstate = states_smacker.Idle(self)

    def get_wall_samples(self, entity):
        return ()

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        if axis == 'y':
            self.currentstate.handle_vertical_contact(entity)
