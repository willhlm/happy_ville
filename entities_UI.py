import pygame
import Read_files, animation, states_health, states_basic, states_buttons
from sys import platform

#for map UI
class Banner():
    def __init__(self,pos,game_objects,type,text):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/UI/map/banner/banner_' + type + '/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.original_pos = pos

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

    def revert(self):#called when quitting map state
        self.rect.topleft = self.original_pos
        self.currentstate.handle_input('Idle')

    def reset_timer(self):
        pass

    def activate(self):#called from map when selecting the pecific banner
        pass#open the local map

#inventory
class Item():#for invenotry, an empty item
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/UI/inventory/item/empty/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(topleft=pos)

        self.dir = [1,0]
        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.description = ''
        self.number = ''#to bilt the number of items player has. THis class is an empty object so no number

class Sword():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/UI/inventory/sword/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(topleft = pos)
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

    def set_level(self,level):
        self.currentstate.set_animation_name('level_'+str(level))

class Infinity_stone():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/UI/inventory/infinity_stone/empty/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

#momamori inventory
class Omamori():#this will save the positions needed to the UI
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/UI/inventory/omamori/empty/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dir = [1,0]

        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

#ability spirit upgrade UI
class Abilities():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        name = type(self).__name__
        self.sprites = Read_files.Sprites_Player('Sprites/UI/abilities/' + name + '/')
        self.image = self.sprites.sprite_dict['idle_1'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.dir = [1,0]

        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.currentstate.set_animation_name('idle_1')

    def activate(self,level):#for UI of Aila abilities
        self.currentstate.set_animation_name('active_'+str(level))
        self.level = level

    def deactivate(self,level):#for UI of Aila abilities
        self.currentstate.set_animation_name('idle_'+str(level))
        self.level = level

    def reset_timer(self):
        pass

class Arrow(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

class Force(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

class Migawari(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['migawari','add extra health to migawari','heals aila when killed','imba']

class Slow_motion(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['slow motion','longer slow motion','slow motion but aila','imba']

class Thunder(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['thunder','hits one additional target','one additional damage','imba']

class Dash(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['dash','free dash','invinsible dash','dash attack']

    def update(self):#called from gameplayHUD
        self.animation.update()
        self.currentstate.update()

class Wall_glide(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['wall glide','free wall jumps','donno','donno']

    def update(self):#called from gameplayHUD
        self.animation.update()
        self.currentstate.update()

class Double_jump(Abilities):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['doulbe jump','free double jump','donno','donno']

    def update(self):#called from gameplayHUD
        self.animation.update()
        self.currentstate.update()

#gameplay HUD
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
        self.sprites = Read_files.Sprites_Player('Sprites/UI/gameplay/movement/hud/')
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites.sprite_dict['idle_1'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        pass

#utilities
class Menu_Arrow():
    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/arrow.png").convert_alpha()
        self.rect = self.img.get_rect()
        self.img.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)

    #note: sets pos to input, doesn't update with an increment of pos like other entities
    def update(self,pos):
        self.rect.topleft = pos

    def draw(self,screen):
        screen.blit(self.img, self.rect.topleft)

class Menu_Box():
    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/box.png").convert_alpha()#select box
        self.rect = self.img.get_rect()

    def update(self,pos):
        pass

    def draw(self,screen):
        pass
        #screen.blit(self.img, self.rect.topleft)

#controllers
class Controllers():
    def __init__(self, pos, game_objects,type):
        self.game_objects = game_objects#animation need it
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate =  getattr(states_buttons, type.capitalize() + '_idle')(self)

    def update(self):
        self.animation.update()

class Xbox(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = Read_files.Sprites_Player('Sprites/UI/controller/xbox/')
        self.image = self.sprites.sprite_dict['a_idle'][0]
        self.rect = self.image.get_rect(topleft=pos)

class Playsation(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = Read_files.Sprites_Player('Sprites/UI/controller/playstation/')
        self.image = self.sprites.sprite_dict['a_idle'][0]
        self.rect = self.image.get_rect(topleft=pos)
