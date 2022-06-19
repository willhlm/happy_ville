import pygame, math, random, sys

class Weather():
    def __init__(self,weather_group,type,number_particles=100):
        self.group = weather_group
        self.create_particles(type,number_particles)

    def create_particles(self,type,number_particles=100):
        for i in range(0,number_particles):
            obj=getattr(sys.modules[__name__], type)()
            self.group.add(obj)

class Sword_effect():
    def __init__(self,group):
        self.group = group

    def create_particles(self,pos,number_particles=100):
        for i in range(0,number_particles):
            obj=Sparks(pos)
            self.group.add(obj)

class Particles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def update(self,scroll):
        self.update_pos(scroll)

    def update_pos(self,scroll):
        self.rect.center = [self.rect.center[0] + scroll[0]+self.velocity[0], self.rect.center[1] + scroll[1]+self.velocity[1]]

    def make_circle(self):
        image = pygame.Surface((2*self.radius,2*self.radius), pygame.SRCALPHA, 32)
        self.image = image.convert_alpha()
        pygame.draw.circle(self.image,self.colour,(self.radius,self.radius),self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def make_sparks(self):
        self.surface = pygame.Surface((10,10), pygame.SRCALPHA, 32).convert_alpha()
        self.image = self.surface
        pygame.draw.polygon(self.image,self.colour,self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def set_color(self):
        replace_color=(251,242,54)#=self.image.get_at((4,4))
        img_copy=pygame.Surface(self.image.get_size())
        img_copy.fill(self.color)
        self.image.set_colorkey(replace_color)#the color key will not be drawn
        img_copy.blit(self.image,(0,0))
        self.image=img_copy
        self.image.set_colorkey((0,0,0,255))

class Sparks(Particles):
    def __init__(self,pos):
        super().__init__()
        self.pos = pos
        self.angle = random.randint(0, 360)
        self.scale = 2
        scale=random.randint(-6, 6)#should maybe depend on the hit direction
        self.velocity = [scale*math.cos(self.angle),scale*math.sin(self.angle)]#[random.randint(-6, 6),random.randint(-6, 6)]#
        self.colour = [255,255,255]

        self.spark_shape()
        self.make_sparks()
        self.lifetime=20#how long the sparks shoud be here

    def speed(self):
        self.angle += 0
        self.velocity[0] -= 0.1
        self.velocity[1] -= 0.1

    def update(self,scroll):
        super().update(scroll)
        self.lifetime-=1
        self.speed()
        self.update_spark()
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            self.kill()

    def update_spark(self):
        self.image = self.surface#reset image
        self.spark_shape()
        pygame.draw.polygon(self.image,self.colour,self.points)

    def spark_shape(self):#potato formula
        self.points = [
        [math.cos(self.angle)*self.velocity[0]*self.scale,math.sin(self.angle)*self.velocity[0]*self.scale],
        [math.cos(self.angle+math.pi*0.5)*self.velocity[0]*self.scale*0.3,math.sin(self.angle+math.pi*0.5)*self.velocity[0]*self.scale*0.3],
        [-math.cos(self.angle)*self.velocity[0]*self.scale*3.5,-math.sin(self.angle)*self.velocity[0]*self.scale*3.5],
        [math.cos(self.angle-math.pi*0.5)*self.velocity[0]*self.scale*0.3,-math.sin(self.angle+math.pi*0.5)*self.velocity[0]*self.scale*0.3]
        ]

class Weather_particles(Particles):
    def __init__(self):
        super().__init__()
        self.pos = [random.randint(-500, 500),random.randint(-500, -100)]#starting position
        self.wind = 2

    def update(self,scroll):
        super().update(scroll)
        self.boundary()
        self.speed()

    def boundary(self):
        if self.rect.y>300:#if on the lower side of screen.
            self.rect.y=random.randint(-500, -100)
        #continiouse falling, horizontally
        if self.rect.x<-100:
            self.rect.x+=500
        elif self.rect.x>500:
            self.rect.x-=500

class Snow(Weather_particles):

    def __init__(self):
        super().__init__()
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
    def __init__(self):
        super().__init__()
        colors=[[255,192,203],[255,105,180],[255,100,180]]
        self.colour=colors[random.randint(0, len(colors)-1)]
        self.make_circle()

class Autumn(Snow):
    def __init__(self):
        super().__init__()
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        self.colour=colors[random.randint(0, len(colors)-1)]
        self.make_circle()

class Rain(Weather_particles):
    def __init__(self):
        super().__init__()
        self.radius = 1
        colors=[[169,139,116],[152,245,255],[61,89,171],[100,149,237]]
        self.colour=colors[random.randint(0, len(colors)-1)]
        self.velocity=[self.wind,3]
        self.make_circle()

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
