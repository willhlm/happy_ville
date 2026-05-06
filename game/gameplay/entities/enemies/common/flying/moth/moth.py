import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.shared.components.stimulus import StimulusTargetSelector
from engine.utils import read_files
from .config import ENEMY_CONFIG as MOTH_CONFIG
from .deciders import AttractionTargetGiveUpDecider, CheckAttractionTargetDecider


MOTH_DECIDERS = {
    'check_attraction_target': CheckAttractionTargetDecider,
    'attraction_target_give_up': AttractionTargetGiveUpDecider,
}

class Moth(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = MOTH_CONFIG['moth']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/moth/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/moth/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]

        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.target_selector = StimulusTargetSelector(self, self.config['stimulus'])
        self.currentstate = StateManager(
            self,
            type='flying',
            custom_deciders=MOTH_DECIDERS,
            universal_states=['death', 'dead', 'hurt', 'wait'],
        )

    def get_state_machine_target(self):
        return self.target_selector.get_target(fallback_target=self.game_objects.player)
