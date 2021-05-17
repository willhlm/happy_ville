import pygame, math, random

weather_paricles=pygame.sprite.Group()

class Weather(pygame.sprite.Sprite):

    number_of_particles=0

    def __init__(self):
        super().__init__()
        self.pos=[random.randint(1, 479),random.randint(-500, -100)]
        self.velocity=[0,0]
        Weather.number_of_particles+=1
        self.phase=random.randint(0, 10)
        self.max=100#max number of partivles

    def update(self,pos,screen):
        pygame.draw.circle(screen,self.color,self.pos,self.radius)#draw a circle

        self.pos = [self.pos[0] + pos[0], self.pos[1] + pos[1]]#compensate for scroll and new speed

        self.speed()#modulate the speed according to the particle type

        if self.pos[1]>300:#if on the lower side of screen. SHould we do ground collisions?
            weather_paricles.remove(self)
            Weather.number_of_particles-=1

        #continiouse falling, horizontally
        if self.pos[0]<0:
            self.pos[0]+=480
        elif self.pos[0]>480:
            self.pos[0]-=480

    def create_particle(self,particle):
        for i in range(self.number_of_particles,self.max):
            if particle=='snow':
                particles=Snow()
                weather_paricles.add(particles)
            elif particle=='sakura':
                particles=Sakura()
                weather_paricles.add(particles)
            elif particle=='rain':
                particles=Rain()
                weather_paricles.add(particles)
            elif particle=='autumn':
                particles=Autumn()
                weather_paricles.add(particles)
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
