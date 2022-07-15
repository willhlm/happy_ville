import pygame, math, random, sys

class Particles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def update(self,scroll):
        self.update_pos(scroll)

    def update_pos(self,scroll):
        self.true_pos= [self.true_pos[0] + scroll[0]+self.velocity[0], self.true_pos[1] + scroll[1]+self.velocity[1]]
        #self.rect.topleft = [self.rect.topleft[0] + scroll[0]+self.velocity[0], self.rect.topleft[1] + scroll[1]+self.velocity[1]]
        self.rect.center = self.true_pos

    def make_circle(self):
        image = pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32)
        self.image = image.convert_alpha()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.true_pos = self.pos

    def make_sparks(self):
        self.spark_shape()#define the shape of spark
        self.surface = pygame.Surface((60,60), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.true_pos = self.pos

class General_particle(Particles):#a general one
    def __init__(self,pos,distance=400,lifetime=60,vel=[7,13],type='spark',dir='isotropic',scale=1):
        super().__init__()
        if dir=='isotropic':
            angle=random.randint(-180, 180)#the ejection anglex

        elif dir < 0:#rigth hit
            spawn_angle = 30
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        else:#left hit
            spawn_angle = 30
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex

        self.angle = -(2*math.pi*angle)/360
        self.scale = scale
        self.distance = distance
        self.lifetime = lifetime
        self.pos = [pos[0]+self.distance*math.cos(self.angle),pos[1]+self.distance*math.sin(self.angle)]
        amp=random.randint(vel[0], vel[1])
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]
        self.fade = 255
        self.colour = [255,255,255,self.fade]

        if type=='spark':
            self.make_sparks()
            self.update_particle=self.update_spark
        else:#circles
            self.update_particle=self.update_circle
            vel = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
            low = max(int(vel*0.3),1)#trying so that higher velocities have larger radius
            self.radius = low
            self.make_circle()

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= 1
        self.speed()
        self.fading()
        self.destroy()
        self.update_particle()

    def speed(self):
        self.velocity[0] -= 0.01*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=5
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def update_circle(self):
        pass

    def update_spark(self):
        self.image = self.surface.copy()
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)

    def spark_shape(self):
        vel=math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
        offsetx=30
        offsety=30

        self.points = [
        [offsetx+math.cos(self.angle)*vel*self.scale,offsety+math.sin(self.angle)*vel*self.scale],
        [offsetx+math.cos(self.angle+math.pi*0.5)*vel*self.scale*0.3,offsety+math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3],
        [offsetx-math.cos(self.angle)*vel*self.scale*3.5,offsety-math.sin(self.angle)*vel*self.scale*3.5],
        [offsetx+math.cos(self.angle-math.pi*0.5)*vel*self.scale*0.3,offsety-math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3]
        ]


class Sword_effects(Particles):
    def __init__(self,pos,dir):
        super().__init__()
        spawn_angle = 30
        if dir > 0:#rigth hit
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        else:#left hit
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex

        self.angle = -(2*math.pi*angle)/360
        self.fade = 255
        self.pos = pos #spawn position
        self.lifetime = 15

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= 1
        self.speed()
        self.fading()
        self.destroy()

    def speed(self):
        self.velocity[0] -= 0.02*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.02*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=40
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

class Sword_sparks(Sword_effects):
    def __init__(self,pos,dir):
        super().__init__(pos,dir)
        self.scale = 1
        amp=random.randint(10, 14)
        self.velocity = [amp*math.cos(self.angle),amp*math.sin(self.angle)]#[random.randint(-6, 6),random.randint(-6, 6)]#
        self.colour = [255,255,255,self.fade]

        self.make_sparks()

    def update(self,scroll):
        super().update(scroll)
        self.update_spark()

    def update_spark(self):
        self.image = self.surface.copy()
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)

    def spark_shape(self):
        vel=math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
        offsetx=30
        offsety=30

        self.points = [
        [offsetx+math.cos(self.angle)*vel*self.scale,offsety+math.sin(self.angle)*vel*self.scale],
        [offsetx+math.cos(self.angle+math.pi*0.5)*vel*self.scale*0.3,offsety+math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3],
        [offsetx-math.cos(self.angle)*vel*self.scale*3.5,offsety-math.sin(self.angle)*vel*self.scale*3.5],
        [offsetx+math.cos(self.angle-math.pi*0.5)*vel*self.scale*0.3,offsety-math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3]
        ]

class Sword_particles(Sword_effects):
    def __init__(self,pos,dir):
        super().__init__(pos,dir)
        amp=random.randint(1, 10)
        self.velocity = [amp*math.cos(self.angle),amp*math.sin(self.angle)]#[random.randint(-6, 6),random.randint(-6, 6)]#
        self.colour = [255,255,255,self.fade]

        vel = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)

        low = max(int(vel/3),1)#trying so that higher velocities have larger radius
        self.radius = low
        self.make_circle()
