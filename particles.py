import pygame, math, random, sys

class Particles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def update(self,scroll):
        self.update_pos(scroll)

    def update_pos(self,scroll):
        self.pos = [self.pos[0] + scroll[0]+self.velocity[0], self.pos[1] + scroll[1]+self.velocity[1]]
        #self.rect.topleft = [self.rect.topleft[0] + scroll[0]+self.velocity[0], self.rect.topleft[1] + scroll[1]+self.velocity[1]]
        self.rect.center = self.pos

    def make_circle(self):
        image = pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32)
        self.image = image.convert_alpha()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def make_sparks(self):
        self.canvas_size = 60
        self.spark_shape()#define the shape of spark
        self.surface = pygame.Surface((self.canvas_size,self.canvas_size), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface.copy()
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

<<<<<<< HEAD
class Sword_effects(Particles):
    def __init__(self,pos,dir, spawn_angle):
        super().__init__()
        #spawn_angle = 40
        if dir[0] > 0:#rigth hit
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        elif dir[0] < 0:#left hit
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex
        elif dir[1] > 0:
            angle=random.randint(90-spawn_angle, 90+spawn_angle)#the ejection anglex
        else:
            angle=random.randint(270-spawn_angle, 270+spawn_angle)#the ejection anglex

        self.angle = -(2*math.pi*angle)/360
        self.fade = 255
        self.pos = pos #spawn position
        self.lifetime = 14
=======
class General_particle(Particles):#a general one
    def __init__(self,pos,distance=400,lifetime=60,vel=[7,13],type='spark',dir='isotropic',scale=1, colour=[255,255,255,255]):
        super().__init__()
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
            self.update_particle=self.update_spark
        else:#circles
            self.update_particle=self.update_circle
            vel = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)
            low = max(int(vel*0.3),1)#trying so that higher velocities have larger radius
            self.radius = low
            self.make_circle()
>>>>>>> e55f523a382630b894b8cee8b0cddf324c855874

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= 1
        self.speed()
        self.fading()
        self.destroy()
        self.update_particle()

    def speed(self):
<<<<<<< HEAD
        self.velocity[0] -= 0.17*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.17*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=5
=======
        self.velocity[0] -= 0.01*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=3
>>>>>>> e55f523a382630b894b8cee8b0cddf324c855874
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()
<<<<<<< HEAD

class Sword_sparks(Sword_effects):
    def __init__(self,pos,dir, spawn_angle = 100):
        super().__init__(pos,dir, spawn_angle)
        self.scale = 0.8
        amp=random.randint(17, 21)
        self.velocity = [amp*math.cos(self.angle),amp*math.sin(self.angle)]#[random.randint(-6, 6),random.randint(-6, 6)]#
        self.fade = 250
        self.colour = [255,255,255,self.fade]

        self.make_sparks()

    def update(self,scroll):
        super().update(scroll)
        self.update_spark()

    def update_spark(self):
        self.image = self.surface.copy()
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.fading()

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

class Weather_particles(Particles):
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.width = self.game_objects.game.WINDOW_SIZE[0] + 0.2*self.game_objects.game.WINDOW_SIZE[0]
        self.height = self.game_objects.game.WINDOW_SIZE[1] + 0.1*self.game_objects.game.WINDOW_SIZE[1]
        self.pos = [random.randint(-int(self.width), int(self.width)),random.randint(-700, -50)]#starting position
        self.wind = 2

    def update(self,scroll):
        super().update(scroll)
        self.boundary()
        self.speed()

    def boundary(self):
        if self.rect.y > self.height:#if on the lower side of screen.
            self.true_pos[1]=random.randint(-700, -50)

        #continiouse falling, horizontally
        if self.true_pos[0]<-100:
            self.true_pos[0] += self.width
        elif self.true_pos[0] > self.width:
            self.true_pos[0] -= self.width

class Snow(Weather_particles):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        self.colour = (255,255,255)
        self.radius = random.randint(1, 3)
        self.make_circle()
        self.phase = random.randint(0, 100)
        self.time = 0
        self.velocity=[math.sin(self.time//10+self.phase),1]

    def speed(self):
        self.time+=1
        self.velocity=[math.sin(self.time//10+self.phase)+self.wind,1]
        if self.time>100:
            self.time=0

class Sakura(Snow):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        colors=[[255,192,203],[255,105,180],[255,100,180]]
        self.colour=colors[random.randint(0, len(colors)-1)]
        self.make_circle()

class Autumn(Snow):
    def __init__(self,game_objects):
        super().__init__(game_objects)
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        self.colour=colors[random.randint(0, len(colors)-1)]
        self.make_circle()

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
=======
>>>>>>> e55f523a382630b894b8cee8b0cddf324c855874
