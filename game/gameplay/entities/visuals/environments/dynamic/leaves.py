import pygame, random, math
from engine.utils import read_files
from .base_dynamic import BaseDynamic
from . import states_weather_particles

class Leaves(BaseDynamic):#leaves from trees
    def __init__(self, pos, game_objects, parallax, size, layer_name, kill = False, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.sprites = Leaves.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_weather_particles.Idle(self)

        self.init_pos = [pos[0]+size[0]*0.5,pos[1]-size[1]*0.5]#center
        self.spawn_size = size
        self.velocity[1] = random.randint(1, 3)

        colours = [[60,179,113,255],[154,205,50,255],[34,139,34,255],[46,139,87,255]]#colourd of the leaves
        self.colour = colours[random.randint(0, len(colours)-1)]

        self.reset()
        self.resetting = {False:self.reset,True:self.kill}[kill]
        self.time = 0
        self.phase = random.randint(0, 100)#for velocity
        self.trans_prob = 100#the higher the number, the lwoer the probabillity for the leaf to flip (probabilty = 1/trans_prob). 0 is 0 %

        self.shader =  game_objects.shaders['colour']

    def draw(self, target):
        self.shader['colour'] = self.colour
        super().draw(target)

    def pool(game_objects):#save the texture in memory for later use
        Leaves.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/environments/weather/leaf'+str(random.randint(1,1))+'/', game_objects)#randomly choose a leaf type

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.update_vel(dt)
        self.colour[-1] -= dt*0.2
        self.colour[-1] = max(self.colour[-1],0)

    def update_vel(self, dt):
        self.velocity[0] += dt*(self.game_objects.weather.wind.velocity[0]  - self.friction[0]*self.velocity[0] + math.sin(self.time*0.1+self.phase)*self.parallax[0]*0.3)
        self.velocity[1] += dt*(self.game_objects.weather.wind.velocity[1] * self.friction[1] - self.friction[1]*self.velocity[1])

    def boundary(self):
        if self.colour[-1] < 5 or self.true_pos[1]-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1] > self.game_objects.game.window_size[1]+50:
            self.resetting()

    def reset(self):
        self.colour[-1] = random.uniform(255*self.parallax[0],255)
        self.velocity[1] = random.uniform(0.2,0.5)
        self.time = 0
        self.true_pos = [self.init_pos[0] + random.uniform(-self.spawn_size[0]*0.5, self.spawn_size[0]*0.5), self.init_pos[1] + random.uniform(-self.spawn_size[1]*0.5,self.spawn_size[1]*0.5)]
        self.rect.topleft = self.true_pos.copy()