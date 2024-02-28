import pygame, math, random
import Read_files, states_weather
from Entities import Animatedentity

class Weather():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.wind = Wind(self)
        self.currentstate = states_weather.Idle(self)

    def create_particles(self, type, parallax, group, number_particles = 20):#called from map loader -> move to map loader
        group.add(Fog(self.game_objects, parallax, number_particles))
        group.add(Vertical_circles(self.game_objects, parallax, number_particles))

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
        img = pygame.Surface([weather.game_objects.game.window_size[0],weather.game_objects.game.window_size[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.rect = img.get_rect()
        self.image = weather.game_objects.game.display.surface_to_texture(img)
        self.sprites = {'idle':[self.image]}
        self.velocity = [0,0]
        self.lifetime = 300
        self.true_pos = [0,0]
        self.shader = None
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def draw_shader(self):#called from group
        pass

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

class Lightning(pygame.sprite.Sprite):#white colour fades out and then in
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.image = pygame.Surface([game_objects.game.window_size[0],game_objects.game.window_size[1]], pygame.SRCALPHA, 32).convert_alpha()
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = [game_objects.camera.scroll[0], game_objects.camera.scroll[1]]
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

class Screen_shader(pygame.sprite.Sprite):#make a layer on screen, then use shaders to generate stuff. Better performance
    def __init__(self, game_objects, parallax):
        super().__init__()
        self.game_objects = game_objects
        self.parallax = parallax

        size = self.set_size()
        width = int(self.game_objects.game.window_size[0] + 2*size)#size of the canvas
        height = int(self.game_objects.game.window_size[1] + 2*size)#size of the canvas

        self.image = self.game_objects.game.display.make_layer((width, height)).texture
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.true_pos = list(self.rect.topleft)
        self.time = 0

    def set_size(self):
        return 0

    def update(self):
        self.time += self.game_objects.game.dt
        self.update_pos()

    def update_pos(self):#do not move the canvas
        self.true_pos = [self.game_objects.camera.scroll[0]*self.parallax[0],self.game_objects.camera.scroll[1]*self.parallax[1]]#(0,0)
        self.rect.topleft = self.true_pos.copy()

class Fog(Screen_shader):
    def __init__(self, game_objects, parallax, num):
        super().__init__(game_objects, parallax)
        self.noise_layer = self.game_objects.game.display.make_layer((self.game_objects.game.window_size[0], self.game_objects.game.window_size[1]))
        self.shader = game_objects.shaders['fog']

    def draw_shader(self):#called before draw in group
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.005
        self.game_objects.shaders['noise_perlin']['u_resolution'] = (640,360)
        self.game_objects.shaders['noise_perlin']['scale'] = (10,10)
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera.scroll[0]*self.parallax[0],self.game_objects.camera.scroll[1]*self.parallax[1]]

        self.game_objects.game.display.render(self.image, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])
        self.shader['noise'] = self.noise_layer.texture
        self.shader['TIME'] = self.time*0.001
        self.shader['scroll'] = [self.game_objects.camera.scroll[0]*self.parallax[0],self.game_objects.camera.scroll[1]*self.parallax[1]]

class Particles_shader(Screen_shader):#particles. Better performance
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax)
        self.number_particles = number_particles#max 20, hard coded in shader
        self.set_parameters()

    def set_size(self):#size of particle
        self.canvas_size = 5 * self.parallax[0]
        return self.canvas_size

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
        self.shader['size'] = self.image.size
        self.shader['gradient'] = 1
        self.shader['number_particles'] = self.number_particles
        self.shader['colour'] = (255,255,255,255)

    def set_parameters(self):#parameters needed for the shader
        self.centers, self.radius, self.phase, self.velocity = [], [], [], []#make a list of stuff keep info as "attributes"
        for i in range(0, self.number_particles):
            x = random.uniform(-self.canvas_size, self.game_objects.game.window_size[0] + self.canvas_size)
            y = random.uniform(-self.canvas_size, self.game_objects.game.window_size[1] + self.canvas_size)
            self.centers.append([x,y])
            self.radius.append(self.canvas_size)
            self.phase.append(random.uniform(-math.pi,math.pi))
            self.velocity.append([0,0])

    def draw_shader(self):
        self.shader['parallax'] = self.parallax
        self.shader['centers'] = self.centers
        self.shader['radius'] = self.radius
        self.shader['scroll'] = self.game_objects.camera.scroll

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [0.5*math.sin(self.time*0.01 + self.phase[i]),-0.5]

    def update_size(self, i):
        self.radius[i] = self.canvas_size * math.sin(self.time*0.01 + self.phase[i]) + self.canvas_size*0.5

class Circles(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)

    def update_vel(self, i):#how it should move
        pass

    def update_size(self,i):
        super().update_size(i)
        if self.radius[i] < 0.1:#if circle is small
            x = random.uniform(0, self.game_objects.game.window_size[0])
            y = random.uniform(0, self.game_objects.game.window_size[1])
            self.centers[i] = [x,y]

class Fireflies(Vertical_circles):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = [255,255,102,150]#circle colour
        self.canvas_size = 3*self.parallax[0]#particle radius, depends on parallax

    def update_vel(self,i):
        self.velocity[i]  = [math.cos(self.time*0.01+self.phase[i]),math.sin(self.time*0.01+self.phase[i])]

class Rain(Particles_shader):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader = self.game_objects.shaders['screen_rectangle']
        self.shader['size'] = self.image.size
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

    def draw_shader(self):
        self.shader['parallax'] = self.parallax
        self.shader['centers'] = self.centers
        self.shader['scroll'] = self.game_objects.camera.scroll

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [-1, 5]

class Snow(Rain):
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__(game_objects, parallax, number_particles)
        self.shader['colour'] = (255,255,255,255)
        self.shader['scale'] = (self.parallax[0]*2,self.parallax[0]*0.33)#to make it square

    def draw_shader(self):
        self.shader['centers'] = self.centers

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
        pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera.scroll[0], self.true_pos[1]-self.parallax[0]*self.game_objects.camera.scroll[1]]
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
        self.sprites = Read_files.load_sprites_dict('Sprites/GFX/twinkle/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)

        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
        self.rect.topleft = self.true_pos
        self.animation.frame = random.randint(0, len(self.sprites['idle'])-1)

    def reset_timer(self):#called when animation finishes
        self.true_pos = [random.randint(0, int(self.width)),random.randint(0, int(self.height))]#starting position
