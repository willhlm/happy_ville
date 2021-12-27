import pygame, math, random, sys

class Weather(pygame.sprite.Sprite):

    def __init__(self,group):
        super().__init__()
        pos=[random.randint(-50, 500),random.randint(-500, -100)]
        self.velocity=[0,0]
        self.phase=random.randint(0, 10)
        self.image = pygame.image.load("Sprites/animations/Weather/particle.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.group=group

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0]+self.velocity[0], self.rect.topleft[1] + pos[1]+self.velocity[1]]

    def update(self,pos):
        self.update_pos(pos)
        self.speed()#modulate the speed according to the particle type
        self.boundary()

    def boundary(self):
        if self.rect.y>300:#if on the lower side of screen. SHould we do ground collisions?
            self.rect.y=random.randint(-500, -100)

        #continiouse falling, horizontally
        if self.rect.x<-50:
            self.rect.x+=500
        elif self.rect.x>500:
            self.rect.x-=500

    def create_particle(self,particle):
        for i in range(0,100):
            obj=getattr(sys.modules[__name__], particle)(self.group)
            self.group.add(obj)

    def set_color(self):
        replace_color=(251,242,54)#=self.image.get_at((4,4))
        img_copy=pygame.Surface(self.image.get_size())
        img_copy.fill(self.color)
        self.image.set_colorkey(replace_color)
        img_copy.blit(self.image,(0,0))
        self.image=img_copy
        self.image.set_colorkey((0,0,0,255))

    def size(self):
        self.image=pygame.transform.scale(self.image,(self.scale[0],self.scale[1]))

    def speed(self):
        pass

class Snow(Weather):
    def __init__(self,group):
        super().__init__(group)
        self.scale=[20,20]
        self.color=(255,255,255)
        self.timer=500
        self.size()
        self.set_color()

    def speed(self):
        self.timer-=1
        self.velocity=[2*math.sin(self.timer//10) + self.phase,1]

class Sakura(Weather):
    def __init__(self,group):
        super().__init__(group)
        self.scale=[20,20]
        colors=[[255,192,203],[255,105,180],[255,100,180]]
        self.color=colors[random.randint(0, len(colors)-1)]
        self.velocity=[self.phase,1.5]
        self.size()
        self.set_color()

class Autumn(Sakura):
    def __init__(self,group):
        super().__init__(group)
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        self.color=colors[random.randint(0, len(colors)-1)]

class Rain(Weather):
    def __init__(self,group):
        super().__init__(group)
        self.scale=[5,40]
        self.color=(0,0,200)
        self.velocity=[0.1,5]
        self.size()
        self.set_color()

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
