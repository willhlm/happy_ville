import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG 
from .states import Accend, Deccend

FLOW_COPTER_STATES = {
    'accend': Accend,
    'deccend': Deccend,
}

class FlowCopter(FlyingEnemy):#is controlled by lyktgubbe
    def __init__(self,pos,game_objects, **kwargs):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['flow_copter']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/flow_copter/',game_objects, flip_x = True)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        #self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/flow_copter/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)

        light_cfg = self.config['light']
        self.light = self.game_objects.lights.add_light(
            self,
            radius=light_cfg['min_radius'],
            colour=[
                light_cfg['colour'][0] / 255,
                light_cfg['colour'][1] / 255,
                light_cfg['colour'][2] / 255,
                0.0,
            ],
        )
        self.currentstate = StateManager(
            self,
            type='flying',
            custom_states=FLOW_COPTER_STATES,
            universal_states=['death', 'dead', 'hurt', 'wait'],
        )

    def on_kill_cleanup(self):
        if self.light is not None:
            self.game_objects.lights.remove_light(self.light)
            self.light = None

    def set_accend_light(self):
        light_cfg = self.config['light']
        self.light.radius = light_cfg['radius']
        self.light.colour[-1] = light_cfg['alpha']

    def update_deccend_light(self, progress):
        light_cfg = self.config['light']
        progress = max(0.0, min(1.0, progress))
        self.light.radius = light_cfg['radius'] - (light_cfg['radius'] - light_cfg['min_radius']) * progress
        self.light.colour[-1] = light_cfg['alpha'] - (light_cfg['alpha'] - light_cfg['fade_floor']) * progress
