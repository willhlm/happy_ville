import pygame, math, random, sys, Read_files, states_weather, animation, states_basic
from Entities import Animatedentity

class Weather():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def create_particles(self,type,parallax,group,number_particles = 20):
        for i in range(0,number_particles):
            obj = getattr(sys.modules[__name__], type)(self.game_objects,parallax)
            group.add(obj)

    def lightning(self):
        self.game_objects.cosmetics.add(Lightning(self.game_objects))

    def fog(self,group):
        group.add(Fog(self.game_objects))

class Fog(pygame.sprite.Sprite):
    def __init__(self,game_objects):
        super().__init__()
        self.image = pygame.Surface([game_objects.game.WINDOW_SIZE[0],game_objects.game.WINDOW_SIZE[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,0)
        self.colour = [255,255,255,5]
        self.draw_rectangle()

    def draw_rectangle(self):
        pygame.draw.rect(self.image,self.colour,self.rect)

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]

    def update(self,scroll):
        self.rect.topleft = (0,0)

class Lightning(pygame.sprite.Sprite):#white colour fades out and then in
    def __init__(self,game_objects):
        super().__init__()
        self.image = pygame.Surface([game_objects.game.WINDOW_SIZE[0]*2,game_objects.game.WINDOW_SIZE[1]*2], pygame.SRCALPHA, 32).convert_alpha()
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect()
        self.rect.center = [game_objects.game.WINDOW_SIZE[0],game_objects.game.WINDOW_SIZE[1]]
        self.count = 0
        self.fade_length = 20
        self.image.set_alpha(int(255/self.fade_length))

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]

    def update(self,scroll):
        self.update_pos(scroll)
        self.update_img()
        self.count += 1
        if self.count > self.fade_length:
            self.kill()

    def update_img(self):
        self.image.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))

class Bound_entity(Animatedentity):#entities bound to the scereen
    def __init__(self,game_objects, parallax):
        super().__init__(pos = [0,0])
        self.game_objects = game_objects
        self.parallax = parallax
        self.width = self.game_objects.game.WINDOW_SIZE[0] + 0.6*self.game_objects.game.WINDOW_SIZE[0]
        self.height = self.game_objects.game.WINDOW_SIZE[1] + 0.6*self.game_objects.game.WINDOW_SIZE[1]
        self.velocity = [0,0]

    def update(self,scroll):
        super().update(scroll)
        self.boundary()

    def update_pos(self,scroll):
        self.true_pos = [self.true_pos[0] + (scroll[0]+self.velocity[0])*self.parallax[0], self.true_pos[1] + (scroll[1]+self.velocity[1])*self.parallax[1]]
        self.rect.topleft = self.true_pos

    def boundary(self):#continiouse falling
        if self.rect.centery > self.height:#if on the lower side of screen.
            self.true_pos[1] -= self.height
        elif self.rect.centery < -100:#if on the higher side of screen.
            self.true_pos[1] += self.height
        elif self.rect.centerx < -100:
            self.true_pos[0] += self.width
        elif self.rect.centerx > self.width:
            self.true_pos[0] -= self.width

#cosmetic particles
class Circles(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.colour = [255,255,255,160]

        self.radius = round(5*self.parallax[0])#particle radius, depends on parallax
        self.layers = 5#number of layers in the glow
        self.glow_radius = self.layers*self.radius#determines the canvas size needed

        self.pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.true_pos = self.pos.copy()
        self.prepare_canvas()
        self.time = 0
        self.phase = random.randint(0, 180)

    def update(self,scroll):
        self.update_pos(scroll)
        self.boundary()
        self.update_image()

    def update_image(self):
        self.image = self.surface.copy()
        self.time += 1
        self.colour[-1] = 80*math.sin(self.time*0.01+self.phase)+80#set fade
        radius = (self.radius*math.sin(self.time*0.01+self.phase)+self.radius)*0.5#modify redious

        self.make_glow(radius)
        pygame.draw.circle(self.image,self.colour,(self.glow_radius,self.glow_radius),radius)

    def prepare_canvas(self):
        self.surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2),pygame.SRCALPHA,32).convert_alpha()
        self.image = self.surface.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def make_glow(self,radius):
        temp = self.surface.copy()
        for i in range(self.layers):
            k = 255
            pygame.draw.circle(temp,(k,k,k,10),self.surface.get_rect().center,i*radius)
            self.image.blit(temp,(0,0))#need to blit in order to "stack" the alpha

class Blink(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/blink/')
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()

        self.pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.true_pos = self.pos.copy()
        self.rect.topleft = self.true_pos

    def reset_timer(self):#called when animation finishes
        self.currentstate.handle_input('Invisible')
        self.true_pos = [random.randint(-100, int(self.width)),random.randint(-50, int(self.height))]#starting position

#weather particles: snow, leaf, rain etc
class Weather_particles(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.pos = [random.randint(0, int(self.width)),random.randint(-700, -50)]#starting position
        self.true_pos = self.pos.copy()

        self.wind = -2
        self.velocity[1] = random.randint(1, 3)
        self.time = 0
        self.phase = random.randint(0, 100)#for velocity

        self.trans_prob = 100#the higher the number, the lwoer the probabillity for the leaf to flip (probabilty = 1/trans_prob). 0 is 0 %

    def update(self,scroll):
        super().update(scroll)
        self.time+=1
        self.currentstate.update()
        self.animation.update()
        self.speed()

    def reset_timer(self):
        self.currentstate.enter_state('Idle')

    def speed(self):
        self.velocity=[math.sin(self.time*0.1+self.phase)+self.wind,self.velocity[1]]

    def set_color(self,new_colour):
        replace_color=(255,0,0)
        for key in self.sprites.keys():
            for image in self.sprites[key]:
                img_copy=pygame.Surface(self.image.get_size())
                img_copy.fill(new_colour)
                image.set_colorkey(replace_color)#the color key will not be drawn
                image.blit(img_copy,(0,0),special_flags=pygame.BLEND_RGB_ADD)

class Sakura(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_weather.Idle(self)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[[255,192,203],[240,128,128],[255,182,193],[221,160,221],[219,112,147]]
        colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(colour)

class Autumn(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_weather.Idle(self)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        colour=colors[random.randint(0, len(colors)-1)]
        self.set_color(colour)

class Snow(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/snow/')
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_weather.Idle(self)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        self.trans_prob = 0#the higher the number, the lwoer the probabillity for the leaf to flip. 0 is 0 %
        self.colour = (255,255,255)
        self.set_color(self.colour)

        self.phase = random.randint(0, 180)

    def speed(self):
        self.velocity=[math.sin(self.time//10+self.phase)+self.wind,self.velocity[1]]

class Rain(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/rain/')
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_weather.Idle(self)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[[10,191,255],[152,245,255],[61,89,171],[100,149,237]]
        self.colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(self.colour)
        self.angle=math.acos(self.wind/6)
        self.scale = 0.5
        amp = random.randint(2, 4)
        self.velocity = [amp*math.cos(self.angle),4]
        self.make_sparks()
        self.trans_prob = 0#the higher the number, the lwoer the probabillity for the leaf to flip. 0 is 0 %

    def speed(self):
        pass
