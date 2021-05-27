import pygame, math, random, sys

weather_paricles=pygame.sprite.Group()

class Weather(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.pos=[random.randint(1, 479),random.randint(-500, -100)]
        self.velocity=[0,0]
        self.phase=random.randint(0, 10)
        self.max=100#max number of partivles

    def update(self,pos,screen):

        pygame.draw.circle(screen,self.color,self.pos,self.radius)#draw a circle
        Light.add_white(10,(30,5,5),screen,self.pos)#light spehre around the particles

        self.pos = [self.pos[0] + pos[0], self.pos[1] + pos[1]]#compensate for scroll and new speed

        self.speed()#modulate the speed according to the particle type

        if self.pos[1]>300:#if on the lower side of screen. SHould we do ground collisions?
            self.pos=[random.randint(1, 479),random.randint(-500, -100)]                

        #continiouse falling, horizontally
        if self.pos[0]<0:
            self.pos[0]+=480
        elif self.pos[0]>480:
            self.pos[0]-=480


    def create_particle(self,particle):
        for i in range(0,self.max):
            obj=getattr(sys.modules[__name__], particle)#make a class based on the name
            weather_paricles.add(obj())
        return weather_paricles

class Snow(Weather):
    def __init__(self):
        super().__init__()
        self.radius=2#size
        self.timer=500#lifetime
        self.color=(255,255,255)

    def speed(self):
        self.timer-=1
        self.velocity=[0.5*math.sin(self.timer//10 + self.phase),0.5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

class Sakura(Weather):
    def __init__(self):
        super().__init__()
        colors=[[255,192,203],[255,105,180],[255,100,180]]
        self.radius=2#size
        self.timer=500#lifetime
        self.color=colors[random.randint(0, len(colors)-1)]

    def speed(self):
        self.timer-=1
        self.velocity=[self.phase,1.5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

class Autumn(Sakura):
    def __init__(self):
        super().__init__()
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        self.color=colors[random.randint(0, len(colors)-1)]

class Rain(Weather):
    def __init__(self):
        super().__init__()
        self.radius=1#size
        self.timer=500#lifetime
        self.color=(0,0,200)

    def speed(self):
        self.timer-=1
        self.velocity=[0.1,5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

class Light():
    def __init__(self):
        super().__init__()
        pass

    @staticmethod
    def add_white(radius,colour,screen,pos):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(pos[0]-radius,pos[1]-radius),special_flags=pygame.BLEND_RGB_ADD)
