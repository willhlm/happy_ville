import pygame
import Read_files, animation, states_health, states_basic, states_buttons
from sys import platform
from Entities import Animatedentity

#for map UI
class Banner(Animatedentity):
    def __init__(self,pos,game_objects,type,text):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/map/banner/banner_' + type + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.original_pos = pos
        #self.blit_text(text)

    def blit_text(self,text):
        screen = self.game_objects.game.display.make_layer((self.image.width,self.image.height))#make a layer ("surface")
        text_surface = self.game_objects.font.render(text = text)
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):
                self.game_objects.game.display.render(image, screen)
                self.game_objects.game.display.render(text_surface, screen, position = (image.width*0.5,image.height*0.5))
                self.sprites[state][frame] = screen

    def update(self,scroll):
        super().update()
        self.update_pos(scroll)

    def update_pos(self,scroll):
        self.rect.center = [self.rect.center[0] + scroll[0], self.rect.center[1] + scroll[1]]

    def revert(self):#called when quitting map state
        self.rect.topleft = self.original_pos
        self.currentstate.handle_input('Idle')

    def activate(self):#called from map when selecting the pecific banner
        pass#open the local map

#inventory
class Item(Animatedentity):#for invenotry, an empty item
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/inventory/item/empty/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''
        self.number = ''#to bilt the number of items player has. THis class is an empty object so no number

class Sword(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/inventory/sword/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

    def set_level(self,level):
        self.currentstate.set_animation_name('level_'+str(level))

class Infinity_stone(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/inventory/infinity_stone/empty/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''

#momamori inventory
class Omamori(Animatedentity):#this will save the positions needed to the UI
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/inventory/omamori/empty/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''

#ability spirit upgrade UI
class Abilities(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        name = type(self).__name__
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/abilities/' + name + '/',game_objects)
        self.image = self.sprites['idle_1'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
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
class Health(Animatedentity):#gameplay UI
    def __init__(self,game_objects):
        super().__init__([0,0],game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/gameplay/health/',game_objects)
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

    def take_dmg(self,dmg):
        self.health -= dmg
        self.health = max(0,self.health)#so that it doesn't go negative, inprinciple not needed
        self.currentstate.handle_input('Hurt')#make heart go white

class Spirit(Animatedentity):#gameplay UI
    def __init__(self,game_objects):
        super().__init__([0,0],game_objects)
        self.sprites=Read_files.load_sprites_dict('Sprites/UI/gameplay/spirit/',game_objects)
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

class Movement_hud():#gameplay UI
    def __init__(self,entity):
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/gameplay/movement/hud/',entity.game_objects)
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites['idle_1'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        pass

#utilities
class Menu_Arrow():
    def __init__(self,game_objects):
        img = pygame.image.load("Sprites/utils/arrow.png").convert_alpha()
        self.rect = img.get_rect()
        img.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.image = game_objects.game.display.surface_to_texture(img)

    #note: sets pos to input, doesn't update with an increment of pos like other entities
    def update(self,pos):
        self.rect.topleft = pos

class Menu_Box():
    def __init__(self, game_objects):
        img = pygame.image.load("Sprites/utils/box.png").convert_alpha()#select box
        self.image = game_objects.game.display.surface_to_texture(img)
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)

    def update(self,pos):
        pass

    def draw(self,screen):
        pass    

#controllers
class Controllers():
    def __init__(self, pos, game_objects,type):
        self.game_objects = game_objects#animation need it
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate =  getattr(states_buttons, type.capitalize() + '_idle')(self)

    def reset_timer(self):#animation neeed it
        pass

    def update(self):
        self.animation.update()

class Xbox(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/controller/xbox/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

class Playstation(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = Read_files.load_sprites_dict('Sprites/UI/controller/playstation/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
