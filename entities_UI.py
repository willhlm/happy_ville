import pygame
import Read_files, animation, states_health, states_basic

class Banner():#for map UI
    def __init__(self,pos,game_objects,type,text):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('UI/map/objects/banner/banner_' + type + '/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos

        self.dir = [-1,0]
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)
        self.blit_text(text)

    def blit_text(self,text):
        text_surface = self.game_objects.font.render(text = text)
        for state in self.sprites.sprite_dict.keys():
            for frame, image in enumerate(self.sprites.sprite_dict[state]):
                image.blit(text_surface,(image.get_width()*0.5,image.get_height()*0.5))
                self.sprites.sprite_dict[state][frame] = image

    def update(self,scroll):
        self.update_pos(scroll)
        self.currentstate.update()
        self.animation.update()

    def update_pos(self,scroll):
        self.rect.center = [self.rect.center[0] + scroll[0], self.rect.center[1] + scroll[1]]

    def reset_timer(self):
        pass

    def activate(self):#called from map when selecting the pecific banner
        pass#open the local map

class Health():#gameplay UI
    def __init__(self,game_objects):
        self.sprites=Read_files.Sprites_Player('Sprites/UI/gameplay/health/')
        self.game_objects = game_objects#animation need it
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_health.Death(self)
        self.health = 0

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def take_dmg(self,dmg):
        self.health -= dmg
        self.health = max(0,self.health)#so that it doesn't go negative, inprinciple not needed
        self.currentstate.handle_input('Hurt')#make heart go white

class Spirit():#gameplay UI
    def __init__(self,game_objects):
        self.sprites=Read_files.Sprites_Player('Sprites/UI/gameplay/spirit/')
        self.game_objects = game_objects
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_health.Death(self)
        self.health = 0

    def update(self):
        self.currentstate.update()
        self.animation.update()

class Movement_hud():#gameplay UI
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/UI/gameplay/movement/hud')
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites.sprite_dict['idle_1'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        pass
