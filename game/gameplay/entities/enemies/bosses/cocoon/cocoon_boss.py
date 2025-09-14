import pygame
from engine.utils import read_files
from gameplay.entities.interactables.cocoon import Cocoon
from . import states_cocoon

class CocoonBoss(Cocoon):#boss cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/cocoon_boss/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.aggro_distance = [200,50]
        self.currentstate = states_cocoon.Idle(self)
        self.item = Tungsten
        self.game_objects.signals.subscribe('who_is_cocoon', self.respond_to_cutscene)#the signal is emitted when the cutscene is initalised

    def respond_to_cutscene(self, callback):
        callback(self)

    def particle_release(self):
        for i in range(0,30):
            obj1 = getattr(particles, 'Circle')(self.rect.center,self.game_objects,distance=0,lifetime=55,vel={'linear':[7,14]},dir='isotropic',scale=0.5,colour = [255,255,255,255])
            self.game_objects.cosmetics.add(obj1)

    def take_dmg(self,projectile):
        if self.flags['invincibility']: return
        self.flags['invincibility'] = True
        self.game_objects.quests_events.initiate_quest('butterfly_encounter')

