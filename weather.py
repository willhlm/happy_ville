import pygame, math, random, sys
import Read_files, states_weather_particles, states_weather
from Entities import Animatedentity

class Weather():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.wind = Wind(self)
        self.currentstate = states_weather.Idle(self)

    def create_particles(self,type,parallax,group,number_particles = 20):#called from map loader
        for i in range(0,number_particles):
            obj = getattr(sys.modules[__name__], type)(self.game_objects,parallax)
            group.add(obj)

    def update(self):
        self.currentstate.update()

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
        self.image = pygame.Surface([game_objects.game.window_size[0],game_objects.game.window_size[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect()
        self.rect.center = [game_objects.game.window_size[0],game_objects.game.window_size[1]]
        self.count = 0
        self.fade_length = 20
        self.image.set_alpha(int(255/self.fade_length))
        self.true_pos = [self.game_objects.camera.scroll[0],self.game_objects.camera.scroll[1]]

    def update(self):
        self.update_img()
        self.count += 1
        if self.count > self.fade_length:
            self.kill()

    def update_img(self):
        self.image.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))

#particles
class Bound_entity(Animatedentity):#entities bound to the scereen, should it be inheriting from animated entities (if we intendo to use animation) or static entity (if we intend to use pygame for particles)
    def __init__(self,game_objects, parallax):
        super().__init__([0,0],game_objects)
        self.parallax = parallax
        self.width = self.game_objects.game.window_size[0] + 0.6*self.game_objects.game.window_size[0]
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
        return
        if self.rect.centerx < -100:
            self.true_pos[0] += self.width
        elif self.rect.centerx > self.width:
            self.true_pos[0] -= self.width
        elif self.rect.centery > self.height:#if on the lower side of screen.
            self.true_pos[1] -= self.height
        elif self.rect.centery < -100:#if on the higher side of screen.
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
        try:#the images are stored in an class variable such that the animations are only made once. This way, many particles can be made with very small performance.
            self.images = type(self).animations[tuple(self.parallax)]
        except:#if it is the first time making that circle size (depends on parallax)
            self.prepare_animation()#make the circles once and store each frame in a list: takes performance to make many
            type(self).animations[tuple(self.parallax)] = self.images

        self.frame = random.randint(0, len(self.images)-1)#randomise the starting frame
        self.animation_speed = 1

    def set_parameters(self):
        self.colour = [255,255,255,160]#center ball colour
        self.glow_colour = [255,255,255,2]#colour of each glow
        self.radius = 4.9*self.parallax[0]#particle radius, depends on parallax

    def update(self):
        self.update_pos()
        self.boundary()
        self.set_image()

    def set_image(self):
        self.image = self.images[int(self.frame)]
        self.frame += self.game_objects.game.dt*self.animation_speed

        if self.frame >= len(self.images):
            self.frame = 0
            #set new positions
            self.true_pos = [random.randint(0, int(self.width))+self.parallax[0]*self.game_objects.camera.scroll[0],random.randint(0, int(self.height))+self.parallax[1]*self.game_objects.camera.scroll[1]]#starting position

    def prepare_animation(self):
        self.prepare_canvas()
        self.frame = 0
        type(self).images = []#store each animation frame
        for i in range(round(1/self.frequency)):#number of frames
            self.prepare_images()
            type(self).images.append(self.image)#store each animation frame

    def prepare_canvas(self):
        self.surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2),pygame.SRCALPHA,32).convert_alpha()
        self.image = self.surface.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

    def prepare_images(self):
        phase = 3*math.pi*0.5
        self.image = self.surface.copy()
        alpha = (self.colour[-1]*math.sin(self.frame*self.frequency*2*math.pi+phase)+self.colour[-1])*0.5#set alpha
        radius = (self.radius*math.sin(self.frame*self.frequency*2*math.pi+phase)+self.radius)*0.5#modify redious
        self.prepare_glow(radius)

        temp = self.surface.copy()
        colour = self.colour[:3]
        colour.append(alpha)
        pygame.draw.circle(temp,colour,(self.glow_radius,self.glow_radius),radius)
        self.image.blit(temp,(0,0))#need to blit in order to "stack" the alpha
        self.frame += 1

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
        self.velocity  = [0.5*math.sin(self.frame*0.1+self.phase),-1]

class Fireflies(Circles):
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.phase = random.randint(0, 360)#randomise the starting phase
        self.animation_speed = 0.8

    def set_parameters(self):
        self.colour = [153,153,0,150]#center ball colour
        self.glow_colour = [255,215,0,2]#colour of each glow
        self.radius = 3*self.parallax[0]#particle radius, depends on parallax

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity  = [math.cos(self.frame*0.01+self.phase),math.sin(self.frame*0.01+self.phase)]

class Blink(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/blink/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()

        self.pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.true_pos = self.pos.copy()
        self.rect.topleft = self.true_pos
        self.animation.frame = random.randint(0, len(self.sprites.sprite_dict['idle']))

    def reset_timer(self):#called when animation finishes
        self.pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.true_pos = self.pos.copy()

#weather particles: snow, leaf, rain etc
class Weather_particles(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.currentstate = states_weather_particles.Idle(self)
        self.true_pos = [random.randint(0, int(self.width)),random.randint(-700, -50)]#starting position

        self.velocity[1] = random.randint(1, 3)
        self.time = 0
        self.phase = random.randint(0, 100)#for velocity

        self.trans_prob = 100#the higher the number, the lwoer the probabillity for the leaf to flip (probabilty = 1/trans_prob). 0 is 0 %
        self.friction = [0.5,0]

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
        size = [self.image.get_size()[0]*self.parallax[0],self.image.get_size()[1]*self.parallax[1]]
        for state in self.sprites.sprite_dict.keys():
            for frame,image in enumerate(self.sprites.sprite_dict[state]):
                img_copy = pygame.transform.scale(image,size)
                arr = pygame.PixelArray(img_copy)#make it an pixel arrat since it has a replace color function
                arr.replace(replace_color,new_colour)
                self.sprites.sprite_dict[state][frame] =arr.make_surface()
                arr.close()

class Sakura(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/leaf'+str(rand)+'/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[[255,192,203],[240,128,128],[255,182,193],[221,160,221],[219,112,147]]
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
        rand=random.randint(1,1)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/weather/rain/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[[10,191,255],[152,245,255],[61,89,171],[100,149,237]]
        self.colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(self.colour)
        self.angle=math.acos(self.wind/6)
        self.scale = 0.5
        amp = random.randint(2, 4)
        self.velocity = [amp*math.cos(self.angle),4]
        self.trans_prob = 0#the higher the number, the lwoer the probabillity for the leaf to flip. 0 is 0 %

    def speed(self):
        pass
