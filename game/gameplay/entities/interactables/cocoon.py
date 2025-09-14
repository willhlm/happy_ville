
import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Cocoon(Interactables):#larv cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/cocoon/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.health = 3
        self.flags = {'invincibility': False}

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        #projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.flags['invincibility']  = True

        if self.health > 0:
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.currentstate.handle_input('Once', animation_name = 'hurt', next_state = 'Idle')
            #self.shader_state.handle_input('Hurt')#turn white
        else:#death
            self.currentstate.handle_input('Once', animation_name = 'interact', next_state = 'Interacted')
            self.game_objects.enemies.add(Maggot(self.rect.center,self.game_objects))

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

