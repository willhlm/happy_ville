import pygame, math, random, sys

class Weather():#maybe should just be a function
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.group = game_objects.weather

    def create_particles(self,type,number_particles=100):
        for i in range(0,number_particles):
            obj = getattr(sys.modules[__name__], type)(self.game_objects)
            self.group.add(obj)

class Absorb_particles():
    def __init__(self,cosmetics_group,pos):
        self.group = cosmetics_group
        self.pos = pos

    def create_particles(self,number_particles = 10):
        for i in range(0,number_particles):
            obj1 = Absorb_particle(self.pos)
            self.group.add(obj1)

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

    def set_color(self):#not using for now
        replace_color=(251,242,54)#=self.image.get_at((4,4))
        img_copy=pygame.Surface(self.image.get_size())
        img_copy.fill(self.colour)
        self.image.set_colorkey(replace_color)#the color key will not be drawn
        img_copy.blit(self.image,(0,0))
        self.image=img_copy
        self.image.set_colorkey((0,0,0,255))

class Absorb_particle(Particles):
    def __init__(self,pos):
        super().__init__()
        angle=random.randint(-180, 180)#the ejection anglex

        self.angle = -(2*math.pi*angle)/360
        self.fade = 255
        self.radius = 400
        self.pos = [pos[0]+self.radius*math.cos(self.angle),pos[1]+self.radius*math.sin(self.angle)]
        self.lifetime = 60

        self.scale = 1
        amp=random.randint(7, 13)
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]#[random.randint(-6, 6),random.randint(-6, 6)]#
        self.colour = [255,255,255,self.fade]

        self.make_sparks()

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= 1
        self.speed()
        self.fading()
        self.destroy()
        self.update_spark()

    def speed(self):
        self.velocity[0] -= 0.01*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=5
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

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
        spawn_angle = 40
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

    def update(self,scroll):
        super().update(scroll)
        self.lifetime -= 1
        self.speed()
        self.fading()
        self.destroy()

    def speed(self):
        self.velocity[0] -= 0.17*self.velocity[0]#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.17*self.velocity[1]#0.1*math.sin(self.angle)

    def fading(self):
        self.fade-=5
        self.image.set_alpha(self.fade)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

class Sword_sparks(Sword_effects):
    def __init__(self,pos,dir):
        super().__init__(pos,dir)
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
        self.radius = 2
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
