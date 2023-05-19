import pygame
import Read_files, animation, states_health, states_basic

#for map UI
class Banner():
    def __init__(self,pos,game_objects,type,text):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('UI/map/objects/banner/banner_' + type + '/')
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
class Item():#for invenotry
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('UI/inventory/objects/item/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.topleft = pos

        self.dir = [1,0]
        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.description = ''
        self.number = ''#to bilt the number of items player has. THis class is an empty object so no number

class Sword():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('UI/inventory/objects/sword/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.topleft = pos
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

class Infinity_stone():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('UI/inventory/objects/infinity_stone/empty')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.topleft = pos
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

#momamori inventory
class Empty_omamori():#this will save the positions needed to the UI
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/empty_omamori/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.dir = [1,0]

        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

#ability spirit upgrade UI
class Abilities_spirit():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        name = type(self).__name__
        self.sprites = Read_files.Sprites_Player('UI/ability_spirit_upgrade/objects/' + name + '/')
        self.image = self.sprites.sprite_dict['idle_1'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.dir = [1,0]

        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

    def activate(self,level):#for UI of Aila abilities
        self.currentstate.enter_state('Active_'+str(level))
        self.level = level

    def deactivate(self,level):#for UI of Aila abilities
        self.currentstate.enter_state('Idle_'+str(level))
        self.level = level

    def reset_timer(self):
        pass

class Arrow(Abilities_spirit):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

class Force(Abilities_spirit):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

class Migawari(Abilities_spirit):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['migawari','add extra health to migawari','heals aila when killed','imba']

class Slow_motion(Abilities_spirit):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['slow motion','longer slow motion','slow motion but aila','imba']

class Thunder(Abilities_spirit):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['thunder','hits one additional target','one additional damage','imba']

class Abilities_movement():
    def __init__(self,pos,game_objects):
        self.game_objects = game_objects
        name = type(self).__name__
        self.sprites = Read_files.Sprites_Player('UI/ability_movement_upgrade/objects/' + name + '/')
        self.image = self.sprites.sprite_dict['idle_1'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.dir = [1,0]

        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle_1(self)#

    def update(self):#called from gameplayHUD
        self.animation.update()
        self.currentstate.update()

    def activate(self,level):#for UI of Aila abilities
        self.currentstate.enter_state('Active_'+str(level))
        self.level = level

    def deactivate(self,level):#for UI of Aila abilities
        self.currentstate.enter_state('Idle_'+str(level))
        self.level = level

    def reset_timer(self):
        pass

class Dash(Abilities_movement):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['dash','free dash','invinsible dash','dash attack']

class Wall_glide(Abilities_movement):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['wall glide','free wall jumps','donno','donno']

class Double_jump(Abilities_movement):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ['doulbe jump','free double jump','donno','donno']

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
        self.sprites = Read_files.Sprites_Player('Sprites/UI/gameplay/movement/hud')
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites.sprite_dict['idle_1'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        pass
