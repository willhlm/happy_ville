import pygame

from engine.utils import read_files
from engine.utils.functions import sign
from gameplay.entities.enemies.base.boss import Boss
from gameplay.entities.enemies.bosses.shared import task_manager
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.projectiles.ranged.poison_blob import PoisonBlob

from .config import TOADESS_CONFIG
from .toadess_states import STATE_REGISTRY

class Toadess(Boss):
    def __init__(self, pos, game_objects, ID=None, initial_state=None, **kwargs):
        super().__init__(pos, game_objects, ID)
        self.config = TOADESS_CONFIG
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/enemies/bosses/toadess/", game_objects, flip_x=True)
        self.sounds = read_files.load_sounds_dict("assets/audio/sfx/entities/enemies/bosses/toadess/")
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 50, 50)

        self.attack_distance = self.config["attack_distance"]
        self.jump_distance = self.config["jump_distance"]
        self.movement_modifier.add_immunity("two_d_liquid")

        self.vitals.set_max_health(self.config["health"])
        self.vitals.set_health(self.vitals.max_health)

        self.phase = 1
        self.pending_phase_transition = False

        selector_config = dict(self.config["selector"])
        if selector_config["mode"] == "deterministic":
            selector_config["pattern_cycle"] = self.get_pattern_cycle_for_phase(1)

        self.currentstate = task_manager.TaskManager(self, STATE_REGISTRY, self.config["patterns"], selector_config)
        initial_state = initial_state or ("off_screen" if ID else "idle")
        self.currentstate.enter_state(initial_state)
        self.dir[0] = -1

    def get_pattern_cycle_for_phase(self, phase):
        return self.config["selector"]["phase_pattern_cycles"][phase]

    def start_encounter_intro(self):
        self.currentstate.clear_tasks()
        for task in self.config["encounter_intro_tasks"]:
            self.currentstate.queue_task(**task)
        self.currentstate.start_next_task()

    def should_enter_phase_2(self):
        if self.phase >= 2: return False            
        phase_2_threshold = self.vitals.max_health * self.config["phase_health_thresholds"]["phase_2"]
        return self.vitals.health <= phase_2_threshold

    def enter_phase_2(self):
        if self.phase >= 2: return            
        self.phase = 2
        self.pending_phase_transition = True
        self.currentstate.set_pattern_cycle(self.get_pattern_cycle_for_phase(self.phase), reset=True)

    def take_dmg(self, effect):
        self.vitals.damage(effect.damage)

        if self.vitals.health > 0:
            if self.should_enter_phase_2():
                self.enter_phase_2()
            self.shader_state.handle_input("hurt")
            self.currentstate.handle_input("hurt")
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=12, scale=0.9)
        else:
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=20, scale=0.95)
            self.currentstate.die()
        return effect

    def start_attack_cooldown(self, attack_name):
        self.flags["attack_able"] = False
        self.game_objects.timer_manager.start_timer(self.config["attack_cooldowns"][attack_name], self.on_attack_timeout)

    def lick_attack(self):
        attack = HurtBox(self, lifetime=30, dir=self.dir, size=[100, 34])
        self.game_objects.projectiles.add_enemy(attack)

    def spit_attack(self):
        direction = [self.dir[0], -1]   
        projectile = PoisonBlob([self.hitbox.centerx, self.hitbox.centery - 10], self.game_objects, dir=direction, amp=[2, 2])        
        self.game_objects.projectiles.add_enemy(projectile)
