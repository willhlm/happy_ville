import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.states import states_basic

class ThunderAura(AnimatedEntity):#the auro around aila when doing the thunder attack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/thunder_aura/',game_objects)
        self.currentstate = states_basic.Once(self,next_state = 'Idle',animation_name='idle')#
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()#pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)

    def update(self, dt):
        super().update(dt)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):#called when animation is finished
        super().reset_timer()
        self.currentstate.handle_input('Idle')
