import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Light_crystal(Interactables):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/light_crystals/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.flags = {'invincibility': False}

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        projectile.clash_particles(self.hitbox.center)
        self.flags['invincibility'] = True
        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.currentstate.handle_input('Transform')
        self.game_objects.lights.add_light(self)#should be when interacted state is initialised and not on taking dmg

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

