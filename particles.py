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
        self.colour = colour
        self.phase = random.uniform(-math.pi,math.pi)#for the cave grass relsease particles
        self.dir = [-1,0]#gruop draw need it

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
        self.colour[-1] -= self.fade_scale*self.game_objects.game.dt
        self.colour[-1] = max(self.colour[-1],0)

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

class Circle(Particles):
    def __init__(self,pos,game_objects,distance,lifetime,vel,dir,scale, colour):
        super().__init__(pos,game_objects,distance,lifetime,vel,dir,scale,colour)
        self.radius = random.randint(max(scale-1,1), round(scale+1))
        self.fade_scale = 0.1#how fast alpha should do down
        self.image = Circle.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos

        self.shader = game_objects.shaders['circle']#draws a circle
        self.shader['size'] = self.image.size
        self.shader['gradient'] = 0#one means gradient, 0 is without

    def draw_shader(self):#his called just before the draw
        self.shader['color'] = self.colour
        self.shader['radius'] = self.radius

    def pool(game_objects):#save the stuff in memory for later use
        Circle.image = game_objects.game.display.make_layer((50,50)).texture

class Spark(Particles):#a general one
    def __init__(self,pos,game_objects,distance,lifetime,vel,dir,scale,colour):
        super().__init__(pos,game_objects,distance,lifetime,vel,dir,scale,colour)
        self.fade_scale = 0.4

        self.image = Spark.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos

        self.shader = game_objects.shaders['spark']
        self.shader['size'] = self.image.size
        self.shader['scale'] = scale

    def draw_shader(self):#called from group draw
        self.shader['colour'] = self.colour
        self.shader['velocity'] =self.velocity

    def pool(game_objects):#save the stuff in memory for later use
        Spark.image = game_objects.game.display.make_layer((50,50)).texture
