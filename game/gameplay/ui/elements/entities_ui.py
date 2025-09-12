import pygame, math
from engine.utils import read_files
from engine.system import animation

from gameplay.entities.states import states_buttons, states_health, states_basic
from gameplay.entities.base.animated_entity import AnimatedEntity

#for map UI
class Banner(AnimatedEntity):
    def __init__(self, pos, game_objects, type, map_text):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/map/banner/banner_' + type + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.original_pos = pos
        self.map_text = map_text
        self.time = 0#for the animation
        #self.blit_text(map_text)

    def blit_text(self,text):
        screen = self.game_objects.game.display.make_layer((self.image.width,self.image.height))#make a layer ("surface")
        text_surface = self.game_objects.font.render(text = text)
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):
                self.game_objects.game.display.render(image, screen)
                self.game_objects.game.display.render(text_surface, screen, position = (image.width*0.5,image.height*0.5))
                self.sprites[state][frame] = screen

    def update_scroll(self, scroll):
        self.rect.center = [self.rect.center[0] + scroll[0], self.rect.center[1] + scroll[1]]

    def update(self, dt):
        super().update(dt)
        self.time += dt * 0.05
        self.update_pos()

    def update_pos(self):
        self.rect.center = [self.rect.center[0], self.rect.center[1] + math.sin(2 * self.time)]

    def activate(self):#called from map when selecting the pecific banner
        return self.map_text

class MapArrow(AnimatedEntity):#for invenotry, the pointer
    def __init__(self, pos, game_objects, map_text, direction):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/map/arrow/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.time = 0
        self.map_text = map_text
        self.original_pos = pos

        if direction == 'left':
            self.angle = 0#angle of the arrow
            self.move_direction = [1,0]
        elif direction == 'right':
            self.angle = 180
            self.move_direction = [1,0]
        elif direction == 'up':
            self.angle = 90
            self.move_direction = [0,1]
        elif direction == 'down':
            self.angle = 270
            self.move_direction = [0,1]

    def activate(self):
        return self.map_text

    def update(self, dt):
        super().update(dt)
        self.time += dt * 0.1
        self.update_pos()

    def update_pos(self):
        self.rect.center = [self.rect.center[0] + 2 * self.move_direction[0] * math.sin(self.time), self.rect.center[1] + 2 * self.move_direction[1] * math.sin(self.time)]

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, angle = self.angle, position = self.rect.topleft)#shader render

    def reset(self):
        self.rect.topleft = self.original_pos
        self.time = 0

class Rooms(AnimatedEntity):#the rroms in map
    def __init__(self, pos, game_objects, number):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/map/rooms/nordveden/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)        
        self.room_number = number

#inventory
class InventoryPointer(AnimatedEntity):#for invenotry, the pointer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/inventory/pointer/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

class InventoryContainer(AnimatedEntity):#for invenotry, will contain items
    def __init__(self, pos, game_objects, item):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/inventory/container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.item = item

    def get_item(self):
        return self.item

class Sword(AnimatedEntity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/inventory/sword/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

    def set_level(self, level):
        self.currentstate.set_animation_name('level_'+str(level))

#radna inventory screen
class Hand(AnimatedEntity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/radna/hand/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

#gameplay HUD
class Health(AnimatedEntity):#gameplay UI
    def __init__(self, game_objects, path = 'assets/sprites/ui/gameplay/health/'):
        super().__init__([0,0],game_objects)
        self.sprites = read_files.load_sprites_dict(path, game_objects)
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

    def take_dmg(self,dmg):
        self.health -= dmg
        self.health = max(0,self.health)#so that it doesn't go negative, inprinciple not needed
        self.currentstate.handle_input('Hurt')#make heart go white

class Health_frame(Health):#gameplay UI
    def __init__(self,game_objects):
        super().__init__(game_objects, 'assets/sprites/ui/gameplay/health_frame/')

class Spirit(AnimatedEntity):#gameplay UI
    def __init__(self,game_objects, path = 'assets/sprites/ui/gameplay/spirit/'):
        super().__init__([0,0],game_objects)
        self.sprites=read_files.load_sprites_dict(path, game_objects)
        self.image = self.sprites['death'][0]
        self.animation.play('death')
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

class Spirit_frame(Spirit):#gameplay UI
    def __init__(self,game_objects):
        super().__init__(game_objects, 'assets/sprites/ui/gameplay/spirit_frame/')

class Movement_hud():#gameplay UI
    def __init__(self,entity):
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/gameplay/ability/frame/',entity.game_objects)
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self, dt):
        pass

class Money_frame(): #HJORTRON!!!!
    def __init__(self,entity):
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/gameplay/money/',entity.game_objects)
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self, dt):
        pass

#utilities
class MenuArrow():
    def __init__(self, pos, game_objects, flip = False):
        self.game_objects = game_objects
        self.image = MenuArrow.image
        self.sounds = MenuArrow.sounds              
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.true_pos = self.rect.topleft
        
        self.time = 0
        self.flip = flip  

        if flip: self.phase = math.pi             
        else: self.phase = 0        

    def pool(game_objects):
        MenuArrow.sounds = read_files.load_sounds_dict('assets/audio/sfx/ui/arrow/')
        img = pygame.image.load("assets/sprites/utils/arrow/arrow_right.png").convert_alpha()
        MenuArrow.image = game_objects.game.display.surface_to_texture(img)

    def update(self, dt):#note: sets pos to input, doesn't update with an increment of pos like other entities
        self.time += dt * 0.1
        self.update_pos()

    def update_pos(self):                
        shift = 0.5 * math.sin(self.time + self.phase)
        self.true_pos = [self.true_pos[0] + shift, self.true_pos[1]]

    def play_SFX(self, state = 'idle', frame = 0, vol = 0.8):        
        self.game_objects.sound.play_sfx(self.sounds[state][frame], vol = vol)

    def set_pos(self, pos):
        self.rect.topleft = pos
        self.true_pos = list(pos)

    def pressed(self, state = 'select'):#when pressing a button
        self.play_SFX(state)

class Menu_Box():
    def __init__(self, game_objects):
        img = pygame.image.load("assets/sprites/utils/box.png").convert_alpha()#select box
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

    def update(self, dt):
        self.animation.update(dt)

class Xbox(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/controller/xbox/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.animation.play('a_idle')
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

class Playstation(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/controller/playstation/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.animation.play('a_idle')
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

class Keyboard(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/controller/playstation/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.animation.play('a_idle')
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
