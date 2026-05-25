import pygame
from engine import constants as C
from engine.utils import read_files
from engine.system import animation
from gameplay.entities.platforms.texture.textured_platform import TexturedPlatform
from . import states_basic

class FlowerPlatform(TexturedPlatform):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/flower/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.animation = animation.Animation(self)        
        self.currentstate = states_basic.Idle(self)
        self.bounce_velocity = 6
        self.jump_boost = abs(self.bounce_velocity / C.jump_vel_player)

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        if axis != 'y' or side != 'bottom':
            return

        self.currentstate.handle_input('land')
        entity.velocity[1] -= self.bounce_velocity

        if entity is not self.game_objects.player:
            return

        entity.currentstate.enter_state('jump', air_timer=0)
        entity.arm_bounce_jump(jump_boost=self.jump_boost)

    def get_wall_samples(self, entity):
        return ()
        
    def get_ceiling_samples(self, entity):
        return ()