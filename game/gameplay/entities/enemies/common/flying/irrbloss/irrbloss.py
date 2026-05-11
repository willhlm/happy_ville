import pygame 
from engine import constants as C
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG 

from .states import Transform, ChargeUp, Torpedo

IRRBLOSS_STATES = {
    'transform': Transform,
    'charge_up': ChargeUp,
    'torpedo': Torpedo,
}

class Irrbloss(FlyingEnemy):#is controlled by lyktgubbe
    def __init__(self,pos,game_objects, **kwargs):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['irrbloss']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/irrbloss/',game_objects, flip_x = True)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        #self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/irrbloss/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.controller_id = kwargs.get('id')
        self.is_controlled = False
        self.torpedo_velocity = [0, 0]
        self.platform_collider.enabled = False
        
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type='flying', custom_states=IRRBLOSS_STATES, universal_states=['death', 'dead', 'wait'])

        self.stimulus = self.game_objects.stimuli.register_source(self, channel='light', radius=300, strength=1.6, falloff=0.0015, tags={'light_emitter'})
        self.game_objects.signals.subscribe('irrbloss_transform', self._on_transform_signal)
        self.game_objects.signals.subscribe('release_irrbloss', self._on_release_signal)

        self.light = self.game_objects.lights.add_light(self, colour = normlaised, radius = 100)
        self.shader_state.add_shader('aura', colour=C.spirit_colour[:3], size=0.3, fall_off=4, noise_intensity=3)

    def on_kill_cleanup(self):
        self.game_objects.signals.unsubscribe('irrbloss_transform', self._on_transform_signal)
        self.game_objects.signals.unsubscribe('release_irrbloss', self._on_release_signal)

        if self.stimulus is not None:
            self.game_objects.stimuli.unregister_source(self.stimulus)
            self.stimulus = None

        if self.light is not None:
            self.game_objects.lights.remove_light(self.light)
            self.light = None        

    def _on_transform_signal(self, source=None, controller_id=None):
        if controller_id is None or self.controller_id is None:
            return
        if controller_id != self.controller_id:
            return
        self.transform(source=source)

    def transform(self, source=None):
        if self.is_controlled:
            return

        self.is_controlled = True
        self.currentstate.enter_state('transform')
        self.shader_state.add_shader('tint', colour=[255, 0, 0, 180])

    def _on_release_signal(self, source=None, controller_id=None):
        if controller_id is None or self.controller_id is None:
            return
        if controller_id != self.controller_id:
            return
        self.release()
    
    def release(self):
        self.is_controlled = False
        self.torpedo_velocity = [0, 0]
        self.velocity = [0, 0]
        self.currentstate.enter_state('patrol')
        self.shader_state.remove_shader('tint')
