import pygame, math, random, sys

class Particles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def update(self,scroll):
        self.update_pos(scroll)

    def update_pos(self,scroll):
        self.pos = [self.pos[0] + scroll[0]+self.velocity[0]*self.game_objects.game.dt, self.pos[1] + scroll[1]+self.velocity[1]*self.game_objects.game.dt]
        #self.rect.topleft = [self.rect.topleft[0] + scroll[0]+self.velocity[0], self.rect.topleft[1] + scroll[1]+self.velocity[1]]
        self.rect.center = self.pos

    def make_circle(self):
        self.surface =pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def make_sparks(self):
        self.canvas_size = 60
        self.surface = pygame.Surface((self.canvas_size,self.canvas_size), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        self.spark_shape()#define the shape of spark
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update_circle(self):
        pass

    def update_spark(self):
        self.image = self.surface.copy()
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)

    def spark_shape(self):
        vel=math.sqrt(self.velocity[0]**2+self.velocity[1]**2)

        self.points = [
        [self.canvas_size*0.5+math.cos(self.angle)*vel*self.scale,self.canvas_size*0.5+math.sin(self.angle)*vel*self.scale],
        [self.canvas_size*0.5+math.cos(self.angle+math.pi*0.5)*vel*self.scale*0.3,self.canvas_size*0.5+math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3],
        [self.canvas_size*0.5-math.cos(self.angle)*vel*self.scale*3.5,self.canvas_size*0.5-math.sin(self.angle)*vel*self.scale*3.5],
        [self.canvas_size*0.5+math.cos(self.angle-math.pi*0.5)*vel*self.scale*0.3,self.canvas_size*0.5-math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3]
        ]

class General_particle(Particles):#a general one
    def __init__(self,pos,game_objects,distance=400,lifetime=60,vel=[7,13],type='spark',dir='isotropic',scale=1, colour=[255,255,255,255]):
        super().__init__()
        self.game_objects = game_objects

        if dir=='isotropic':
            angle=random.randint(-180, 180)#the ejection anglex
        elif dir == -1:#rigth hit
            spawn_angle = 30
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        elif dir == 1:#left hit
            spawn_angle = 30
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex
        else:#integer
            sign=random.randint(0,1)
            dir=dir+180*sign
            spawn_angle = 10
            angle=random.randint(dir-spawn_angle, dir+spawn_angle)#the ejection anglex

        self.angle = -(2*math.pi*angle)/360
        self.distance = distance
        self.lifetime = lifetime
        self.pos = [pos[0]+self.distance*math.cos(self.angle),pos[1]+self.distance*math.sin(self.angle)]
        amp=random.randint(vel[0], vel[1])
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]
        self.fade = colour[-1]
        self.colour = colour

        if type=='spark':
            self.scale = scale
            self.make_sparks()
            self.update_particle = self.update_spark
        else:#circles
            self.update_particle = self.update_circle
            vel = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
            self.radius = random.randint(max(scale-1,1), scale+1)
            self.make_circle()

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= self.game_objects.game.dt
        self.speed()
        self.fading()
        self.destroy()
        self.update_particle()

    def speed(self):
        self.velocity[0] -= 0.01*self.velocity[0]*self.game_objects.game.dt#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]*self.game_objects.game.dt#0.1*math.sin(self.angle)

    def fading(self):
        self.fade -= 3*self.game_objects.game.dt
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()
