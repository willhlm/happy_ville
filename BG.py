import pygame, math, random

weather=pygame.sprite.Group()

class Background(pygame.sprite.Sprite):

    number_of_particles=0

    def __init__(self):
        super().__init__()
        self.pos=[random.randint(0, 400),random.randint(-400, -100)]
        self.velocity=[0,0]
        Background.number_of_particles+=1

class Snow(Background):
    def __init__(self):
        super().__init__()
        self.radius=2#size
        self.timer=500#lifetime
        self.phase=random.randint(0, 10)

    def update(self,pos,screen):
        pygame.draw.circle(screen,(255,255,255),self.pos,self.radius)#draw a circle

        self.timer-=1
        self.velocity=[0.5*math.sin(self.timer//10 + self.phase),0.5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

        self.pos = [self.pos[0] + pos[0], self.pos[1] + pos[1]]#compensate for scroll

        if self.pos[1]>300:#if on the lower side of screen
            weather.remove(self)
            Background.number_of_particles-=1


def create_particle(number_of_particles,max):
    #if number_of_particles<max:#maybe can be changed to a for loop somehow
    for i in range(number_of_particles,max):
        particles=Snow()
        weather.add(particles)
    return weather
