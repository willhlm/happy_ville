import pygame

from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.shared.components.collision.surface_stick_physics import SurfaceStickPhysics
from engine.utils import read_files

from .config import ENEMY_CONFIG
from .states import Crawl, Hurt

LARV_WALL_STATES = {
    'crawl': Crawl,
    'hurt': Hurt,
}

class LarvWall(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv_wall']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/slime_wall/', game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.angle = 0
        self.friction = self.config['friction'].copy()
        self.health = self.config['health']
        self.clockwise = 1
        movement_config = self.config['movement']
        self.surface_stick_physics = SurfaceStickPhysics(
            self,
            speed=self.config['speeds']['crawl'],
            stick_speed=movement_config['stick_speed'],
            probe_distance=movement_config['probe_distance'],
            corner_inset=movement_config['corner_inset'],
        )
        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_WALL_STATES, custom_deciders = None)
        self.dir[0] = -self.clockwise

    def update_vel(self, dt):
        self.surface_stick_physics.update_velocity()

    def on_ramp_collision(self, side, ramp):
        super().on_ramp_collision(side, ramp)
        self.surface_stick_physics.register_contact(side, ramp)

    def on_platform_side_collision(self, side, block, collision_type='Wall'):
        super().on_platform_side_collision(side, block, collision_type)
        self.surface_stick_physics.register_contact(side, block)

    def on_platform_vertical_collision(self, side, block):
        super().on_platform_vertical_collision(side, block)
        self.surface_stick_physics.register_contact(side, block)

    def draw(self, target):
        self.blit_pos = [int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]), int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0, shader = self.shader)
