import pygame, math, random, sys
import Read_files, states_weather_particles, states_weather
from Entities import Animatedentity

class Weather():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.wind = Wind(self)
        self.currentstate = states_weather.Idle(self)

    def create_particles(self,type,parallax,group,number_particles = 50):#called from map loader
        for i in range(0,number_particles):
            obj = getattr(sys.modules[__name__], type)(self.game_objects,parallax)
            group.add(obj)

    def update(self):
        self.currentstate.update()#bloew the wind from time to time

    def lightning(self):
        self.game_objects.cosmetics.add(Lightning(self.game_objects))

    def blow(self,dir = [-1,0]):#called from currentstate
        self.wind.blow(dir)
        self.game_objects.cosmetics.add(self.wind)

class Wind(pygame.sprite.Sprite):
    def __init__(self,weather):
        super().__init__()
        self.weather = weather
        self.image = pygame.Surface([weather.game_objects.game.window_size[0],weather.game_objects.game.window_size[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        self.velocity = [0,0]
        self.lifetime = 300
        self.true_pos = [0,0]

    def blow(self,dir):#called when weather is initiated
        self.velocity = dir

    def update(self):
        self.lifetime -= self.weather.game_objects.game.dt
        if self.lifetime < 0:
            self.finish()

    def finish(self):
        self.weather.currentstate.handle_input('Finish')
        self.velocity = [0,0]
        self.lifetime = 300
        self.kill()

    def update_pos(self):#not used
        self.true_pos = [self.true_pos[0] + self.velocity[0], self.true_pos[1] + self.velocity[1]]
        self.rect.topleft = self.true_pos

class Fog(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pass

class Lightning(pygame.sprite.Sprite):#white colour fades out and then in
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.image = pygame.Surface([game_objects.game.window_size[0],game_objects.game.window_size[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = [game_objects.camera.scroll[0],game_objects.camera.scroll[1]]
        self.count = 0
        self.fade_length = 20
        self.image.set_alpha(int(255/self.fade_length))

    def update(self):
        self.update_img()
        self.update_pos()
        self.count += self.game_objects.game.dt
        if self.count > self.fade_length:
            self.kill()

    def update_pos(self):
        self.rect.topleft = [self.game_objects.camera.scroll[0],self.game_objects.camera.scroll[1]]

    def update_img(self):
        self.image.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))

#particles
class Bound_entity(Animatedentity):#entities bound to the scereen, should it be inheriting from animated entities (if we intendo to use animation) or static entity (if we intend to use pygame for particles)
    def __init__(self,game_objects, parallax):
        super().__init__([0,0],game_objects)
        self.parallax = parallax
        self.width = self.game_objects.game.window_size[0] + 100
        self.height = self.game_objects.game.window_size[1] + 0.6*self.game_objects.game.window_size[1]
        self.velocity = [0,0]

    def update(self):
        super().update()
        self.update_pos()
        self.boundary()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.parallax[0], self.true_pos[1] + self.velocity[1]*self.parallax[1]]
        self.rect.topleft = self.true_pos.copy()

    def boundary(self):#continiouse falling
        pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera.scroll[0], self.true_pos[1]-self.parallax[0]*self.game_objects.camera.scroll[1]]
        if pos[0] < -100:
            self.true_pos[0] += self.width
        elif pos[0] > self.width:
            self.true_pos[0] -= self.width
        elif pos[1] > self.height:#if on the lower side of screen.
            self.true_pos[1] -= self.height
        elif pos[1] < -100:#if on the higher side of screen.
            self.true_pos[1] += self.height

class Circles(Bound_entity):
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.set_parameters()
        self.layers = 40#number of layers in the glow
        self.glow_spacing_factor = 0.1#a factor to determine the spacing between the glows
        self.glow_radius = self.layers*self.radius*self.glow_spacing_factor#determines the canvas size needed (the size of the largest glow)

        self.true_pos = [random.randint(0, int(self.width))+self.parallax[0]*self.game_objects.camera.scroll[0],random.randint(0, int(self.height))+self.parallax[1]*self.game_objects.camera.scroll[1]]#starting position

        self.frequency = 0.003#the frequncy of grow and shrinking
        if not type(self).animations.get(tuple(self.parallax),False):#the images are stored in an class variable such that the animations are only made once. This way, many particles can be made with very small performance.
            #if it is the first time making that circle size (depends on parallax)
            type(self).animations[tuple(self.parallax)] = self.prepare_animation()#make the circles once and store each frame in a list: takes performance to make many

        images = type(self).animations[tuple(self.parallax)]
        self.sprites = Read_files.Sprites_images({'idle':images})
        self.animation.frame = random.randint(0, len(images)-1)

    def set_parameters(self):
        self.colour = [255,255,255,160]#center ball colour
        self.glow_colour = [255,255,255,2]#colour of each glow
        self.radius = 4.9*self.parallax[0]#particle radius, depends on parallax

    def reset_timer(self):#caled when animation is finished
        self.true_pos = [random.randint(0, int(self.width))+self.parallax[0]*self.game_objects.camera.scroll[0],random.randint(0, int(self.height))+self.parallax[1]*self.game_objects.camera.scroll[1]]#starting position

    def prepare_animation(self):
        self.prepare_canvas()
        images = []#store each animation frame
        for i in range(round(1/self.frequency)):#number of frames
            self.prepare_images(i)
            images.append(self.image)#store each animation frame
        return images

    def prepare_canvas(self):
        self.surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2),pygame.SRCALPHA,32).convert_alpha()
        self.image = self.surface.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

    def prepare_images(self,i):
        phase = 3*math.pi*0.5
        self.image = self.surface.copy()
        alpha = (self.colour[-1]*math.sin(i*self.frequency*2*math.pi+phase)+self.colour[-1])*0.5#set alpha
        radius = (self.radius*math.sin(i*self.frequency*2*math.pi+phase)+self.radius)*0.5#modify redious
        self.prepare_glow(radius)

        temp = self.surface.copy()
        colour = self.colour[:3]
        colour.append(alpha)
        pygame.draw.circle(temp,colour,(self.glow_radius,self.glow_radius),radius)
        self.image.blit(temp,(0,0))#need to blit in order to "stack" the alpha

    def prepare_glow(self,radius):
        temp = self.surface.copy()
        for i in range(self.layers):
            pygame.draw.circle(temp,self.glow_colour,self.surface.get_rect().center,i*radius*self.glow_spacing_factor)
            self.image.blit(temp,(0,0))#need to blit in order to "stack" the alpha

class Vertical_circles(Circles):
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.phase = random.randint(0, 360)#randomise the starting phase

    def set_parameters(self):
        self.colour = [255,255,255,100]#center ball colour
        self.glow_colour = [255,255,255,2]#colour of each glow
        self.radius = 4.9*self.parallax[0]#particle radius, depends on parallax

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity  = [0.5*math.sin(self.animation.frame*0.1+self.phase),-1]

class Fireflies(Circles):
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.phase = random.randint(0, 360)#randomise the starting phase

    def set_parameters(self):
        self.colour = [153,153,0,150]#center ball colour
        self.glow_colour = [255,215,0,2]#colour of each glow
        self.radius = 3*self.parallax[0]#particle radius, depends on parallax

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity  = [math.cos(self.animation.frame*0.01+self.phase),math.sin(self.animation.frame*0.01+self.phase)]

class Twinkle(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/GFX/twinkle/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()

        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.rect.topleft = self.true_pos
        self.animation.frame = random.randint(0, len(self.sprites.sprite_dict['idle'])-1)

    def reset_timer(self):#called when animation finishes
        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position

#weather particles: snow, leaf, rain etc
class Weather_particles(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.currentstate = states_weather_particles.Idle(self)
        self.true_pos = [random.uniform(0, int(self.width)),random.uniform(-700, -50)]#starting position

        self.velocity[1] = random.randint(1, 3)
        self.time = 0
        self.phase = random.randint(0, 100)#for velocity

        self.trans_prob = 100#the higher the number, the lwoer the probabillity for the leaf to flip (probabilty = 1/trans_prob). 0 is 0 %
        self.friction = [0.5,0]
        self.size_scale = parallax.copy()

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        self.update_vel()

    def update_vel(self):
        self.velocity[0] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[0] - self.friction[0]*self.velocity[0] + self.speed())
        self.velocity[1] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[1] - self.friction[1]*self.velocity[1])

    def speed(self):
        return math.sin(self.time*0.1+self.phase)

    def set_color(self,new_colour):
        replace_color = (255,0,0)
        size = [self.image.get_size()[0]*self.size_scale[0],self.image.get_size()[1]*self.size_scale[1]]
        for state in self.sprites.sprite_dict.keys():
            for frame,image in enumerate(self.sprites.sprite_dict[state]):
                img_copy = pygame.transform.scale(image,size)
                arr = pygame.PixelArray(img_copy)#make it an pixel arrat since it has a replace color function
                arr.replace(replace_color,new_colour)
                self.sprites.sprite_dict[state][frame] = arr.make_surface()
                arr.close()

class Sakura(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[(255,192,203),(240,128,128),(255,182,193),(221,160,221),(219,112,147)]
        colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(colour)

class Autumn(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        colour=colors[random.randint(0, len(colors)-1)]
        self.set_color(colour)

class Snow(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/weather/snow/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        self.trans_prob = 0#the higher the number, the lwoer the probabillity for the leaf to flip. 0 is 0 %
        self.colour = (255,255,255)
        self.set_color(self.colour)

        self.phase = random.randint(0, 180)

    def speed(self):
        self.velocity=[math.sin(self.time//10+self.phase)+self.wind,self.velocity[1]]

class Rain(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/rain/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos
        self.size_scale = [1,1]

        colours=[(10,191,255),(152,245,255),(61,89,171),(100,149,237)]
        self.colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(self.colour)
        self.velocity = [0,random.uniform(5, 10)]
        self.trans_prob = 0#the higher the number, the lwoer the probabillity for the leaf to flip. 0 is 0 %

    def speed(self):
        return -1#always drife backwards
