import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files

class Shroompoline(Enemy):#an enemy or interactable?
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/shroompolin/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box = pygame.Rect(pos[0],pos[1],32,10)
        self.flags['aggro'] = False#player collision
        self.flags['invincibility'] = True

    def player_collision(self, player):
        if self.game_objects.player.velocity[1] > 0:#going down
            offset = self.game_objects.player.velocity[1] + 1
            if self.game_objects.player.hitbox.bottom < self.jump_box.top + offset:
                self.currentstate.enter_state('Hurt')
                self.game_objects.player.velocity[1] = -10
                player.flags['shroompoline'] = True
                self.game_objects.player.currentstate.enter_state('Jump_main')
                self.game_objects.timer_manager.start_timer(C.shroomjump_timer_player, player.on_shroomjump_timout)#adds a timer to timer_manager and sets self.invincible to false after a while

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

    def chase(self):#called from AI: when chaising
        pass

    def patrol(self,position):#called from AI: when patroling
        pass