import pygame, math, random
import read_files
from entities import Animatedentity
from states import states_weather

class Weather():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.currentstate = states_weather.Idle(self)      
        self.velocity = [0, 0]#wind velocity -> leaves etc reads this velocity. the wind can change the velocity. 

    def update(self):
        self.currentstate.update()#bloew the wind from time to time

    def flash(self, **kwarg):#lightning        
        self.game_objects.cosmetics.add(Flash(self.game_objects, **kwarg))

    def blow(self, **kwarg):#called from currentstate
        self.game_objects.cosmetics.add(Wind(self.game_objects, **kwarg))

class Screen_shader(pygame.sprite.Sprite):#make a layer on screen, then use shaders to generate stuff. Better performance
    def __init__(self, game_objects, parallax):
        super().__init__()
        self.game_objects = game_objects
        self.parallax = parallax
        self.time = 0

    @classmethod
    def set_size(cls):
        return 0

    def update(self):
        self.time += self.game_objects.game.dt

    def draw(self, target):
        self.game_objects.game.display.render(self.image.texture, target, shader = self.shader)#shader render

    @classmethod
    def pool(cls, game_objects):
        size = cls.set_size()
        width = int(game_objects.game.window_size[0] + 2*size)#size of the canvas
        height = int(game_objects.game.window_size[1] + 2*size)#size of the canvas
        cls.image = game_objects.game.display.make_layer((width, height))

    def release_texture(self):
        pass

class Wind(Screen_shader):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, kwarg.get('parallax', [1,1]))
        self.noise_layer = Wind.noise_layer
        self.shader = game_objects.shaders['wind']
        self.velocity = kwarg.get('velocity', [-2,0.1])#velocity of tw wind lines
        self.lifetime = kwarg.get('lifetime', 500)  

        game_objects.weather.velocity = self.velocity.copy()
        self.channel = self.game_objects.sound.play_sfx(self.sounds['idle'][0], loop = -1, fade = 1000, vol = 0.2)

    @classmethod
    def pool(cls, game_objects):
        cls.image = game_objects.game.display.make_layer(game_objects.game.window_size)
        cls.noise_layer = game_objects.game.display.make_layer(cls.image.size)
        cls.sounds = read_files.load_sounds_dict('audio/SFX/environment/wind/')

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:            
            self.kill()
    
    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.01
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],-self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [1,30]#long in x, short in y
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.shader['noiseTexture'] = self.noise_layer.texture
        self.shader['time'] = self.time * 0.01
        self.shader['velocity'] = self.velocity
        self.shader['lifetime'] = self.lifetime
        super().draw(target)

    def kill(self):
        super().kill()
        self.game_objects.sound.fade_sound(self.channel)
        self.game_objects.weather.velocity = [0,0]    
        self.game_objects.weather.currentstate.handle_input('finish')

class Flash(Screen_shader):#white colour fades out and then in
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, kwarg.get('parallax', [1,1]))
        self.fade_length = 100
        self.image.clear(255,255,255,int(170/self.fade_length))
        self.shader = None
        self.add_light_source()
 
    def add_light_source(self):
        radius = self.game_objects.game.window_size[0] * 0.5
        position = [self.game_objects.camera_manager.camera.scroll[0] + self.game_objects.game.window_size[0] * 0.5, self.game_objects.camera_manager.camera.scroll[1] + self.game_objects.game.window_size[1]*0.5]#put a bg light in center
        self.hitbox = pygame.Rect(0, 0, self.game_objects.game.window_size[0], self.game_objects.game.window_size[1])#for the light source
        self.hitbox.center = position
        self.light = self.game_objects.lights.add_light(target = self ,radius = radius, fade = True, lifetime = True)#put a bg light in center        

    def update_image(self):
        alpha = int((self.fade_length - self.time)*(255/self.fade_length))
        self.image.clear(255,255,255,alpha)
        self.hitbox.center = [self.game_objects.camera_manager.camera.scroll[0] + self.game_objects.game.window_size[0] * 0.5, self.game_objects.camera_manager.camera.scroll[1] + self.game_objects.game.window_size[1]*0.5]#put a bg light in center

    def update(self):
        super().update()
        self.update_image()
        if self.time > self.fade_length:
            self.kill()
            self.game_objects.lights.remove_light(self.light)

class Fog(Screen_shader):
    def __init__(self, game_objects, parallax, num):
        super().__init__(game_objects, parallax)
        self.shader = game_objects.shaders['fog']

    @classmethod
    def pool(cls, game_objects):
        super().pool(game_objects)
        cls.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)

    def draw(self, target):#called before draw in group
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.005
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['scale'] = (10,10)
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0]*self.parallax[0],self.game_objects.camera_manager.camera.scroll[1]*self.parallax[1]]

        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])
        self.shader['noise'] = self.noise_layer.texture
        self.shader['TIME'] = self.time*0.001
        self.shader['fog_color'] = (0, 0, 0, 1)
        self.shader['scroll'] = [self.game_objects.camera_manager.camera.scroll[0]*self.parallax[0],self.game_objects.camera_manager.camera.scroll[1]*self.parallax[1]]
        super().draw(target)

class Particles_shader(Screen_shader):#particles. Better performance
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax)
        self.number_particles = number_particles#max 20, hard coded in shader
        self.set_parameters()

    @classmethod
    def set_size(cls):#size of particle
        return 5

    def set_parameters(self):#set stuff specific for the particles
        pass

    def update(self):
        super().update()
        self.update_partciles()

    def update_partciles(self):
        for i in range(0,self.number_particles):
            self.update_vel(i)
            self.update_centers(i)
            self.update_size(i)

    def update_vel(self, i):#should they move?
        pass

    def update_centers(self, i):
        self.centers[i] = [self.centers[i][0] + self.game_objects.game.dt*self.velocity[i][0]*self.parallax[0], self.centers[i][1] - self.game_objects.game.dt*self.velocity[i][1]*self.parallax[1]]

    def update_size(self, i):#should they change size?
        pass

class Vertical_circles(Particles_shader):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader = self.game_objects.shaders['screen_circles']
        self.shader['size'] = self.image.texture.size
        self.shader['gradient'] = 1
        self.shader['number_particles'] = self.number_particles
        self.shader['colour'] = (255,255,255,255)

    def set_parameters(self):#parameters needed for the shader
        self.centers, self.radius, self.phase, self.velocity = [], [], [], []#make a list of stuff keep info as "attributes"
        self.canvas_size = 5 * self.parallax[0]
        for i in range(0, self.number_particles):
            x = random.uniform(-self.canvas_size, self.game_objects.game.window_size[0] + self.canvas_size)
            y = random.uniform(-self.canvas_size, self.game_objects.game.window_size[1] + self.canvas_size)
            self.centers.append([x,y])
            self.radius.append(self.canvas_size)
            self.phase.append(random.uniform(-math.pi,math.pi))
            self.velocity.append([0,0])

    def draw(self, target):
        self.shader['parallax'] = self.parallax
        self.shader['centers'] = self.centers
        self.shader['radius'] = self.radius
        self.shader['scroll'] = self.game_objects.camera_manager.camera.scroll
        super().draw(target)

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [0.5*math.sin(self.time*0.01 + self.phase[i]),-0.5]

    def update_size(self, i):
        self.radius[i] = self.canvas_size * math.sin(self.time*0.01 + self.phase[i]) + self.canvas_size*0.5

class Circles(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [0.5*math.sin(self.time*0.01 + self.phase[i]),0.5*math.cos(self.time*0.001 + self.phase[i])]

    def update_size(self,i):
        super().update_size(i)
        if self.radius[i] < 0.1:#if circle is small
            x = random.uniform(0, self.game_objects.game.window_size[0])
            y = random.uniform(0, self.game_objects.game.window_size[1])
            self.centers[i] = [x,y]

class Ominous_circles(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = (100, 30, 30, 255)

class Moss_circles(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = (30, 100, 30, 255)

class Fireflies(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = [255,255,102,150]#circle colour

    def update_vel(self,i):
        self.velocity[i]  = [math.cos(self.time*0.01+self.phase[i]),math.sin(self.time*0.01+self.phase[i])]

class Rain(Particles_shader):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader = self.game_objects.shaders['screen_rectangle']
        self.shader['size'] = self.image.texture.size
        self.shader['number_particles'] = self.number_particles
        self.shader['angle'] = 0#rotation angle of the rectangle
        colours=[(10,191,255,255),(152,245,255,255),(61,89,171,255),(100,149,237,255)]
        self.shader['colour'] = colours[random.randint(0, len(colours)-1)]
        self.shader['scale'] = (self.parallax[0],self.parallax[0])

    def set_parameters(self):#parameters needed for the shader
        self.canvas_size = self.parallax[0]
        self.centers, self.velocity = [], []#make a list of stuff keep info as "attributes"
        for i in range(0, self.number_particles):
            x = random.uniform(-self.canvas_size, self.game_objects.game.window_size[0] + self.canvas_size)
            y = random.uniform(-self.canvas_size, self.game_objects.game.window_size[1] + self.canvas_size)
            self.centers.append([x,y])
            self.velocity.append([0,0])

    def draw(self, target):
        self.shader['parallax'] = self.parallax
        self.shader['centers'] = self.centers
        self.shader['scroll'] = self.game_objects.camera_manager.camera.scroll
        super().draw(target)

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [-1, 5]

class Snow(Rain):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = (255,255,255,255)
        self.shader['scale'] = (self.parallax[0]*2,self.parallax[0]*0.33)#to make it square

    def draw(self, target):
        self.shader['centers'] = self.centers
        super().draw(target)

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [0.5*math.cos(self.time*0.01), 1]

#particles from files
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
        self.true_pos = [self.true_pos[0] + self.game_objects.game.dt*self.velocity[0]*self.parallax[0], self.true_pos[1] + self.game_objects.game.dt*self.velocity[1]*self.parallax[1]]
        self.rect.topleft = self.true_pos.copy()

    def boundary(self):#continiouse falling
        pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]]
        if pos[0] < -100:
            self.true_pos[0] += self.width
        elif pos[0] > self.width:
            self.true_pos[0] -= self.width
        elif pos[1] > self.height:#if on the lower side of screen.
            self.true_pos[1] -= self.height
        elif pos[1] < -100:#if on the higher side of screen.
            self.true_pos[1] += self.height

class Twinkle(Bound_entity):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.sprites = read_files.load_sprites_dict('Sprites/GFX/twinkle/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)

        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.rect.topleft = self.true_pos
        self.animation.frame = random.randint(0, len(self.sprites['idle'])-1)

    def reset_timer(self):#called when animation finishes
        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
