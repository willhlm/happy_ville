import pygame, math, random

class Particles(pygame.sprite.Sprite):
    def __init__(self, pos, game_objects, distance = 400, lifetime = 60, vel = {'linear':[7,13]}, dir = 'isotropic', scale = 1, colour = [255,255,255,255]):
        super().__init__()
        self.game_objects = game_objects
        angle = self.define_angle(dir)
        self.angle = -(2*math.pi*angle)/360
        self.lifetime = lifetime
        self.true_pos = [pos[0]+distance*math.cos(self.angle),pos[1]+distance*math.sin(self.angle)]

        motion = list(vel.keys())[0]#linear moetion or wave motion
        self.update_velocity = {'linear':self.linear,'wave':self.wave}[motion]
        amp = random.randint(vel[motion][0], vel[motion][1])
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]
        self.fade = colour[-1]
        self.colour = colour
        self.scale = scale
        self.phase = random.uniform(-math.pi,math.pi)#for the cave grass relsease particles
        self.shader = None
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self):
        self.update_pos()
        self.lifetime -= self.game_objects.game.dt
        self.update_velocity()
        self.fading()
        self.destroy()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.game_objects.game.dt, self.true_pos[1] + self.velocity[1]*self.game_objects.game.dt]
        self.rect.center = self.true_pos

    def wave(self):
        self.velocity  = [0.5*math.sin(self.lifetime*0.1 + self.angle + self.phase),-1]

    def linear(self):
        self.velocity[0] -= 0.01*self.velocity[0]*self.game_objects.game.dt#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]*self.game_objects.game.dt#0.1*math.sin(self.angle)

    def fading(self):
        return
        self.fade -= self.fade_scale*self.game_objects.game.dt
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def define_angle(self,dir):#is there a better way?
        if dir=='isotropic':
            angle=random.randint(-180, 180)#the ejection anglex
        elif dir == -1:#rigth hit
            spawn_angle = 30
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        elif dir == 1:#left hit
            spawn_angle = 30
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex
        else:#integer
            dir += 180*random.randint(0,1)
            spawn_angle = 10
            angle=random.randint(dir-spawn_angle, dir+spawn_angle)#the ejection anglex
        return angle

class Circle(Particles):#a general one
    def __init__(self,pos,game_objects,distance,lifetime,vel,dir,scale, colour):
        super().__init__(pos,game_objects,distance,lifetime,vel,dir,scale,colour)
        self.radius = random.randint(max(self.scale-1,1), round(self.scale+1))
        self.fade_scale = 3
        self.make_circle()
        self.image = self.game_objects.game.display.surface_to_texture(self.image)

    def make_circle(self):
        self.surface =pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.true_pos

class Spark(Particles):#a general one
    def __init__(self,pos,game_objects,distance,lifetime,vel,dir,scale,colour):
        super().__init__(pos,game_objects,distance,lifetime,vel,dir,scale,colour)
        self.make_sparks()
        self.fade_scale = 10
        self.image = self.game_objects.game.display.surface_to_texture(self.image)

    def update(self):
        super().update()
        self.update_spark()

    def update_spark(self):
        self.image = self.surface.copy()
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.image = self.game_objects.game.display.surface_to_texture(self.image)

    def spark_shape(self):
        vel = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)

        self.points = [
        [self.canvas_size*0.5+math.cos(self.angle)*vel*self.scale,self.canvas_size*0.5+math.sin(self.angle)*vel*self.scale],
        [self.canvas_size*0.5+math.cos(self.angle+math.pi*0.5)*vel*self.scale*0.3,self.canvas_size*0.5+math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3],
        [self.canvas_size*0.5-math.cos(self.angle)*vel*self.scale*3.5,self.canvas_size*0.5-math.sin(self.angle)*vel*self.scale*3.5],
        [self.canvas_size*0.5+math.cos(self.angle-math.pi*0.5)*vel*self.scale*0.3,self.canvas_size*0.5-math.sin(self.angle+math.pi*0.5)*vel*self.scale*0.3]
        ]

    def make_sparks(self):
        self.canvas_size = 60
        self.surface = pygame.Surface((self.canvas_size,self.canvas_size), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
        self.spark_shape()#define the shape of spark
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.true_pos
