import pygame
import read_files, animation
import math
from sys import platform
from states import states_buttons, states_health, states_basic
from entities import Animatedentity

#for map UI
class Banner(Animatedentity):
    def __init__(self,pos,game_objects,type,text):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/map/banner/banner_' + type + '/', game_objects)
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
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/item/empty/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''
        self.number = ''#to bilt the number of items player has. THis class is an empty object so no number

class Sword(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/sword/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

    def set_level(self, level):
        self.currentstate.set_animation_name('level_'+str(level))

class Infinity_stone(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/infinity_stone/empty/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''

class Amber_droplet(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/amber_droplet/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = 'moneyyyyy'

class Bone(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/bone/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = 'boner'

#momamori inventory
class Omamori(Animatedentity):#this will save the positions needed to the UI
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/omamori/empty/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.description = ''

    def render_UI(self, target):
        pass

class Necklace(Animatedentity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/inventory/necklace/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

    def set_level(self,level):
        self.currentstate.set_animation_name('level_'+str(level))

#gameplay HUD
class Health(Animatedentity):#gameplay UI
    def __init__(self,game_objects):
        super().__init__([0,0],game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/gameplay/health/',game_objects)
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
        self.sprites=read_files.load_sprites_dict('Sprites/UI/gameplay/spirit/',game_objects)
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

class Movement_hud():#gameplay UI
    def __init__(self,entity):
        self.sprites = read_files.load_sprites_dict('Sprites/UI/gameplay/movement/hud/',entity.game_objects)
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites['idle_1'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        pass

#utilities
class Menu_Arrow():
    def __init__(self, pos, game_objects, offset = [0,0], mirrored = False, animate = False):
        self.game_objects = game_objects
        self.image = Menu_Arrow.image
        self.sounds = Menu_Arrow.sounds
        self.offset = offset
        self.mirrored = mirrored
        self.time = 0
        self.aniamte = animate
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.rect.midright = [pos[0] + self.offset[0], pos[1] + self.offset[1]]
        if mirrored: self.rect.midleft = [pos[0] - self.offset[0], pos[1] + self.offset[1]]
        self.pos_ref = self.rect.center

    def pool(game_objects):
        Menu_Arrow.sounds = read_files.load_sounds_dict('audio/SFX/UI/arrow/')
        img = pygame.image.load("Sprites/utils/arrow_elf.png").convert_alpha()
        Menu_Arrow.image = game_objects.game.display.surface_to_texture(img)

    def update(self):#note: sets pos to input, doesn't update with an increment of pos like other entities
        pass

    def animate(self):
        if self.animate:
            amp = 5
            self.time += self.game_objects.game.dt
            _T = 0.08
            d = amp*math.pow(math.sin(self.time * _T) + 1, 0.5)
            print(d)
            if self.mirrored:
                self.rect.center = [self.pos_ref[0] + d, self.pos_ref[1]]
            else:
                self.rect.center = [self.pos_ref[0] - d, self.pos_ref[1]]

    def play_SFX(self, state = 'idle', frame = 0, vol = 0.8):
        self.game_objects.sound.play_sfx(self.sounds[state][frame], vol = vol)

    def update_pos(self, pos):
        if self.mirrored:
            self.rect.midleft = [pos[0] - self.offset[0], pos[1] + self.offset[1]]
        else:
            self.rect.midright = [pos[0] + self.offset[0], pos[1] + self.offset[1]]
        self.pos_ref = self.rect.center

    def pressed(self, state = 'select'):#when pressing a button
        self.play_SFX(state)

class Menu_arrow_anime(Animatedentity):
    def __init__(self, pos, game_objects, offset = [0,0], mirrored = False):
        super().__init__([0,0],game_objects)
        self.sprite = Menu_arrow_anime.sprites
        self.image = self.sprites['idle'][0]
        self.offset = offset
        self.mirrored = mirrored
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.midright = [pos[0] + self.offset[0], pos[1] + self.offset[1]]
        if mirrored: self.rect.midleft = [pos[0] - self.offset[0], pos[1] + self.offset[1]]

    def pool(game_objects):
        Menu_arrow_anime.sprites = read_files.load_sprites_dict('Sprites/utils/arrow/',game_objects)
        Menu_arrow_anime.sounds = read_files.load_sounds_dict('audio/SFX/UI/arrow/')

    def update(self):#note: sets pos to input, doesn't update with an increment of pos like other entities
        pass

    def play_SFX(self, state = 'idle', frame = 0, vol = 0.8):
        self.game_objects.sound.play_sfx(self.sounds[state][frame], vol = vol)

    def update_pos(self, pos):
        if self.mirrored:
            self.rect.midleft = [pos[0] - self.offset[0], pos[1] + self.offset[1]]
        else:
            self.rect.midright = [pos[0] + self.offset[0], pos[1] + self.offset[1]]

    def pressed(self, state = 'select'):#when pressing a button
        self.play_SFX(state)

class Menu_Box():
    def __init__(self, game_objects):
        img = pygame.image.load("Sprites/utils/box.png").convert_alpha()#select box
        self.image = game_objects.game.display.surface_to_texture(img)
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)

    def update(self,pos):
        pass

    def draw(self,screen):
        pass

class Button():
    def __init__(self, game_objects, **kwarg):
        self.position = kwarg.get('position', (0,0))
        self.image = kwarg.get('image', None)
        self.rect = pygame.Rect(self.position, [self.image.width, self.image.height])
        if kwarg.get('center', None):
            self.rect.center = self.position

    def hoover(self):
        pass

    def pressed(self):
        pass

#controllers
class Controllers():
    def __init__(self, pos, game_objects,type):
        self.game_objects = game_objects#animation need it
        self.animation = animation.Animation(self)
        self.currentstate =  getattr(states_buttons, type.capitalize() + '_idle')(self)

    def reset_timer(self):#animation neeed it
        pass

    def update(self):
        self.animation.update()

class Xbox(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/controller/xbox/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

class Playstation(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/controller/playstation/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

class Keyboard(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/controller/playstation/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
