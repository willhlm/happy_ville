import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from .contained_component import ContainedComponent
from .config import ENEMY_CONFIG as MAGGOT_CONFIG
from .deciders import CheckPlayerCrossOverDecider, CheckPlayerFarDecider
from .states import Contained, Fall, Idle, Land, RunAway

MAGGOT_STATES = {
    "contained": Contained,
    "fall": Fall,
    "land": Land,
    "idle": Idle,
    "run_away": RunAway,
}

MAGGOT_DECIDERS = {
    "check_player_cross_over": CheckPlayerCrossOverDecider,
    "check_player_far": CheckPlayerFarDecider,
}

class Maggot(Enemy):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.config = MAGGOT_CONFIG["maggot"]
        self.contained_component = None
        self.spawn_anchor = kwargs.get("spawn_anchor", 'topleft')
        self.sprites = read_files.load_sprites_dict(
            "assets/sprites/entities/enemies/common/ground/maggot/",
            game_objects,
        )
        self.sounds = read_files.load_sounds_dict(
            "assets/audio/sfx/entities/enemies/common/ground/maggot/"
        )
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self._apply_spawn_anchor(pos, self.spawn_anchor)
        self.currentstate = StateManager(
            self,
            type="ground",
            custom_states=MAGGOT_STATES,
            custom_deciders=MAGGOT_DECIDERS,
        )
        self.vitals.set_max_health(self.config["health"])
        self.vitals.set_health(self.vitals.max_health)

        if kwargs.get("initial_state") == "contained":
            self.contained_component = ContainedComponent(self, kwargs["anchor_pos"])
            self.contained_component.enter_initial_state()

    def _apply_spawn_anchor(self, pos, spawn_anchor):
        if spawn_anchor == "midtop":
            self.rect.midbottom = pos
            self.hitbox.midbottom = pos

    def release_from_container(self):
        self.contained_component.release()
