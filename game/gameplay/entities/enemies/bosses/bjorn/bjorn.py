import random, pygame
from engine.utils import read_files
from gameplay.entities.enemies.base.boss import Boss
from gameplay.entities.enemies.bosses.shared import task_manager
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.shared.components.projectile_spawn_request_tracker import ProjectileSpawnRequestTracker

from .bjorn_states import STATE_REGISTRY
from .config import BJORN_CONFIG

class Bjorn(Boss):
    def __init__(self, pos, game_objects, ID=None, **kwargs):
        super().__init__(pos, game_objects, ID)
        self.config = BJORN_CONFIG
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/enemies/bosses/bjorn/", game_objects, flip_x=True)
        self.sounds = read_files.load_sounds_dict("assets/audio/sfx/entities/enemies/bosses/bjorn/")
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.attack_distance = self.config["attack_distance"]
        self.jump_distance = self.config["jump_distance"]

        self.vitals.set_max_health(self.config["health"])
        self.vitals.set_health(self.vitals.max_health)

        self.currentstate = task_manager.TaskManager(self, STATE_REGISTRY, self.config["patterns"], self.config["selector"])
        self.currentstate.enter_state(self.config["initial_state"])
        self.projectile_spawn_tracker = ProjectileSpawnRequestTracker()

    def attack(self):
        attack = HurtBox(self, lifetime=10, dir=self.dir, size=[64, 32])
        self.game_objects.projectiles.add_enemy(attack)

    def slam(self):
        self.projectile_spawn_tracker.track(
            self.game_objects.areas.request_projectile_spawns(
                "bjorn_slam",
                count=10,
                selector='all',
                fallback_projectile_id='falling_rock',
                warning_interval=6,
                spawn_interval=40,
                spawn_origin='offscreen',
                warning_particle_type='falling_debris_warning',
            )
        )

    def start_wake_intro(self):
        self.currentstate.clear_tasks()
        for task in self.config["wake_intro_tasks"]:
            self.currentstate.queue_task(**task)
        self.currentstate.start_next_task()

    def set_cooldown(self, cooldown_name):
        cooldown = self.config["cooldowns"][cooldown_name]
        self.currentstate.cooldowns.set(cooldown_name, random.randint(cooldown[0], cooldown[1]))

    def killed(self):
        self.projectile_spawn_tracker.cancel_all()
        super().killed()
