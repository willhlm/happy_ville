import pygame

from engine.utils import read_files
from gameplay.entities.enemies.base.boss import Boss
from gameplay.entities.enemies.bosses.shared import task_manager

from .config import PLANTIS_CONFIG
from .states import STATE_REGISTRY


class Plantis(Boss):
    def __init__(self, pos, game_objects, ID=None, initial_state=None, **kwargs):
        super().__init__(pos, game_objects, ID)
        self.config = PLANTIS_CONFIG
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/enemies/bosses/plantis/", game_objects, flip_x=True)
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(0, 0, 42, 52)
        self.hitbox.midbottom = self.rect.midbottom

        self.attack_distance = self.config["attack_distance"]
        self.jump_distance = self.config["jump_distance"]
        self.vitals.set_max_health(self.config["health"])
        self.vitals.set_health(self.vitals.max_health)

        self.currentstate = task_manager.TaskManager(
            self,
            STATE_REGISTRY,
            self.config["patterns"],
            self.config["selector"],
        )
        initial_state = initial_state or "idle"
        self.currentstate.enter_state(initial_state)
        self.dir[0] = -1
        self.flags["aggro"] = False
        self.hit_component.set_invincibility(True)

    def start_encounter_intro(self):
        self.currentstate.clear_tasks()
        for task in self.config["encounter_intro_tasks"]:
            self.currentstate.queue_task(**task)
        self.currentstate.start_next_task()

    def start_aggro(self, delay=0):
        self.flags["aggro"] = True
        self.hit_component.set_invincibility(False)
        super().start_aggro(delay)

    def dead(self):
        self.game_objects.world_controller.golden_fields.windmills.activate("windmill_1")
        super().dead()
        self.death_effects.start_visual()
