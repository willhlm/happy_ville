import pygame, math, random, sys, Read_files, states_weather
from Entities import Animatedentity

class Weather():#maybe should just be a function
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def create_particles(self,type,number_particles=100):
        for i in range(0,number_particles):
            obj = getattr(sys.modules[__name__], type)(self.game_objects)
            self.game_objects.weather.add(obj)

class Weather_particles(Animatedentity):
    def __init__(self,game_objects):
        super().__init__(pos=[0,0])
        self.game_objects = game_objects
        self.currentstate = states_weather.Idle(self)
        self.width = self.game_objects.game.WINDOW_SIZE[0] + 0.6*self.game_objects.game.WINDOW_SIZE[0]
        self.height = self.game_objects.game.WINDOW_SIZE[1] + 0.1*self.game_objects.game.WINDOW_SIZE[1]
        self.pos = [random.randint(0, int(self.width)),random.randint(-700, -50)]#starting position
        self.wind = -2
        self.vel_y = random.randint(1, 3)

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0]+self.velocity[0], self.rect.topleft[1] + scroll[1]+self.velocity[1]]

    def update(self,scroll):
        super().update(scroll)
        self.boundary()

    def boundary(self):
        if self.rect.centery > self.height:#if on the lower side of screen.
            self.rect.centery=random.randint(-700, -50)

        #continiouse falling, horizontally
        elif self.rect.centerx < -100:
            self.rect.centerx += self.width
        elif self.rect.centerx > self.width:
            self.rect.centerx -= self.width

    def set_color(self,new_colour):
        replace_color=(255,0,0)
        for key in self.sprites.keys():
            for image in self.sprites[key]:
                img_copy=pygame.Surface(self.image.get_size())
                img_copy.fill(new_colour)
                image.set_colorkey(replace_color)#the color key will not be drawn
                image.blit(img_copy,(0,0),special_flags=pygame.BLEND_RGB_ADD)

class Leafs(Weather_particles):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.phase = random.randint(0, 100)
        self.speed()

    def speed(self):
        self.velocity=[math.sin(self.currentstate.time//10+self.phase)+self.wind,self.vel_y]

class Snow(Weather_particles):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        self.colour = (255,255,255)
        self.radius = random.randint(1, 3)
        self.make_circle()
        self.phase = random.randint(0, 180)
        self.speed()

    def speed(self):
        self.velocity=[math.sin(self.currentstate.time//10+self.phase)+self.wind,self.vel_y]

    def make_circle(self):
        image = pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32)
        self.image = image.convert_alpha()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

class Sakura(Leafs):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        colours=[[255,192,203],[240,128,128],[255,182,193],[221,160,221],[219,112,147]]
        colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(colour)

class Autumn(Snow):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        colour=colors[random.randint(0, len(colors)-1)]
        self.set_color(colour)

class Rain(Weather_particles):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        colors=[[10,191,255],[152,245,255],[61,89,171],[100,149,237]]
        self.colour=colors[random.randint(0, len(colors)-1)]

        self.angle=math.acos(self.wind/6)
        self.scale = 0.5
        amp = random.randint(2, 4)
        self.velocity = [amp*math.cos(self.angle),4]#[random.randint(-6, 6),random.randint(-6, 6)]#

        self.make_sparks()

    def speed(self):
        pass

    def make_sparks(self):
        self.spark_shape()#define the shape of spark
        self.surface = pygame.Surface((60,60), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.true_pos = self.pos

    def spark_shape(self):
        offsetx=30
        offsety=30

        self.points = [
        [offsetx+math.cos(self.angle)*self.scale,offsety+math.sin(self.angle)*self.scale],
        [offsetx+math.cos(self.angle+math.pi*0.5)*self.scale*0.3,offsety+math.sin(self.angle+math.pi*0.5)*self.scale*0.3],
        [offsetx-math.cos(self.angle)*self.scale*3.5,offsety-math.sin(self.angle)*self.scale*3.5],
        [offsetx+math.cos(self.angle-math.pi*0.5)*self.scale*0.3,offsety-math.sin(self.angle+math.pi*0.5)*self.scale*0.3]
        ]

class Reflection():
    def __init__(self):
        pass

    def draw(self, gamescreen):
        rect = pygame.Rect(25, 25, 100, 50)#size and position of interest
        sub = gamescreen.subsurface(rect)#cut off the interest

        reflection_image = pygame.transform.flip(sub, False, True)#flip in y
        offset=60
        position=[250,100+offset]
        gamescreen.blit(reflection_image,position,special_flags=pygame.BLEND_RGBA_MULT)
