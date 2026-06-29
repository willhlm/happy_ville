import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.shared.components.projectile_spawn_request_tracker import ProjectileSpawnRequestTracker
from gameplay.entities.visuals.cosmetics import ShockWave
from engine.utils import read_files
from .config import ENEMY_CONFIG
from .states import Alert, AttackMain, AttackPre, Drop, Hanging


BAT_STATES = {
    'hanging': Hanging,
    'drop': Drop,
    'alert': Alert,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
}

class Bat(FlyingEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['bat']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/bat/', game_objects)
        self.image = self.sprites['hanging'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, custom_states=BAT_STATES, type='flying', universal_states=['dead', 'death'])
        self.time = 0
        self.projectile_spawn_tracker = ProjectileSpawnRequestTracker()

    def attack(self):
        attack_cfg = self.config['attack']
        self.projectile_spawn_tracker.track(
            self.game_objects.areas.request_projectile_spawns(
                'bat_crystal',
                count=1,
                selector='nearest_to_player',
                fallback_projectile_id='crystal_tagg',
                projectile_kwargs={'velocity': attack_cfg['crystal_velocity'].copy()},
                warning_interval=6,
                spawn_interval=40,
                target_mode='player_x',
                target_offset=attack_cfg['spawn_offset'],
                spawn_origin='area',
                warning_particle_type='falling_debris_warning',
            )
        )

    def emit_scream_wave(self):
        attack_cfg = self.config['attack']        
        self.scream_wave = ShockWave(
            self.hitbox.center,
            self.game_objects,
            size=tuple(attack_cfg['shockwave_size']),
            reference_size=attack_cfg['shockwave_reference_size'],
            alpha=attack_cfg['shockwave_alpha'],
            alpha_decay=attack_cfg['shockwave_alpha_decay'],
            speed=attack_cfg['shockwave_speed'],
            frequency=attack_cfg['shockwave_frequency'],
            width=attack_cfg['shockwave_width'],
            fade=attack_cfg['shockwave_fade'],
            radial_fade_power=attack_cfg['shockwave_radial_fade_power'],
            noise_map_scale=tuple(attack_cfg['shockwave_noise_map_scale']),
            noise_scale=attack_cfg['shockwave_noise_scale'],
            noise_strength=attack_cfg['shockwave_noise_strength'],
            colour=tuple(attack_cfg['shockwave_colour']),
            sine_scale=attack_cfg['shockwave_sine_scale'],
        )
        self.game_objects.cosmetics.add(self.scream_wave)

    def stop_scream_effects(self):
        self.scream_wave.stop_emitting()

    def killed(self):
        self.projectile_spawn_tracker.cancel_all()
        super().killed()

    def on_kill_cleanup(self):
        self.stop_scream_effects()
