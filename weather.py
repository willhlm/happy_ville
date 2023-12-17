import pygame, math, random, sys
import Read_files, states_weather_particles, states_weather
from Entities import Animatedentity

class Weather():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.wind = Wind(self)
        self.currentstate = states_weather.Idle(self)

    def create_particles(self,type,parallax,group,number_particles = 20):#called from map loader
        #for i in range(0,number_particles):
        #    obj = getattr(sys.modules[__name__], type)(self.game_objects,parallax)
        group.add(Screen_particles(self.game_objects,parallax,number_particles))

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

class Screen_particles(pygame.sprite.Sprite):
    def __init__(self,game_objects, parallax, number_particles):
        super().__init__()
        self.game_objects = game_objects
        self.parallax = parallax

        self.number_particles = number_particles#max 20, hard coded in shader
        self.centers, self.radius, self.phase, self.velocity = [], [], [], []
        self.max_radius = 10*parallax[0]
        for i in range(0, self.number_particles):
            x = random.uniform(-self.max_radius, self.game_objects.game.window_size[0] + self.max_radius)
            y = random.uniform(-self.max_radius, self.game_objects.game.window_size[1] + self.max_radius)
            self.centers.append([x,y])
            self.radius.append(self.max_radius)
            self.phase.append(random.uniform(-math.pi,math.pi))
            self.velocity.append([0,0])

        self.width = int(self.game_objects.game.window_size[0] + 2*self.max_radius)
        self.height = int(self.game_objects.game.window_size[1] + 2*self.max_radius)

        self.image = self.game_objects.game.display.make_layer((self.width,self.height)).texture
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.true_pos = list(self.rect.topleft)

        self.shader = self.game_objects.shaders['circles']
        self.shader['size'] = self.image.size
        self.shader['gradient'] = 1
        self.shader['number_particles'] = self.number_particles
        self.shader['colour'] = (255,255,255,255)

        self.temp_scroll = self.game_objects.camera.true_scroll.copy()
        self.shift = [0,0]#an attribute so that first frame wil be [0,0]
        self.time = 0

    def update(self):
        self.time += self.game_objects.game.dt
        self.update_pos()
        self.update_partciles()

    def update_pos(self):
        self.true_pos = [self.game_objects.camera.scroll[0]*self.parallax[0]-self.max_radius,self.game_objects.camera.scroll[1]*self.parallax[1]-self.max_radius]#(0,0)
        self.rect.topleft = self.true_pos.copy()

    def update_partciles(self):
        for i in range(0,self.number_particles):
            self.update_vel(i)
            self.update_centers(i)
            self.update_radius(i)

        self.shift = [self.temp_scroll[0] - self.game_objects.camera.true_scroll[0],self.temp_scroll[1] - self.game_objects.camera.true_scroll[1]]#shift in pixels
        self.temp_scroll = self.game_objects.camera.true_scroll.copy()

    def update_centers(self, i):
        new_pos = [self.centers[i][0] + self.shift[0] + self.game_objects.game.dt*self.velocity[i][0]*self.parallax[0], self.centers[i][1] - self.shift[1] - self.game_objects.game.dt*self.velocity[i][1]*self.parallax[1]]
        self.centers[i] = self.boundary(new_pos)

    def update_radius(self, i):
        self.radius[i] = self.max_radius * math.sin(self.time*0.01 + self.phase[i]) + self.max_radius*0.5
        if self.radius[i] < 1:
            x = random.uniform(0, self.game_objects.game.window_size[0])
            y = random.uniform(0, self.game_objects.game.window_size[1])
            self.centers[i] = [x,y]

    def update_vel(self, i):
        self.velocity[i]  = [0.5*math.sin(self.time*0.01 + self.phase[i]),-1]

    def draw_shader(self):
        self.shader['centers'] = self.centers
        self.shader['radius'] = self.radius

    def boundary(self, new_pos):#continiouse falling
        if new_pos[0] < -self.max_radius:
            new_pos[0] += self.width+ self.max_radius
        elif new_pos[0] > self.width + self.max_radius:
            new_pos[0] -= self.width+ self.max_radius
        elif new_pos[1] > self.height + self.max_radius:#if on the lower side of screen.
            new_pos[1] -= self.height+ self.max_radius
        elif new_pos[1] < -self.max_radius:#if on the higher side of screen.
            new_pos[1] += self.height+ self.max_radius
        return new_pos

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


class Circles(Bound_entity):#shader circles
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.set_parameters()
        self.true_pos = [random.randint(0, int(self.width))+self.parallax[0]*self.game_objects.camera.scroll[0],random.randint(0, int(self.height))+self.parallax[1]*self.game_objects.camera.scroll[1]]#starting position
        self.time = 0

    def update(self):
        self.time += self.game_objects.game.dt*0.01
        self.update_vel()
        self.update_pos()
        self.boundary()

    def set_parameters(self):
        self.colour = [255,255,255,160]#center ball colour
        self.max_radius = 3*self.parallax[0]#particle radius, depends on parallax

    def reset_timer(self):#caled when animation is finished
        self.true_pos = [random.randint(0, int(self.width))+self.parallax[0]*self.game_objects.camera.scroll[0],random.randint(0, int(self.height))+self.parallax[1]*self.game_objects.camera.scroll[1]]#starting position

class Vertical_circles(Circles):
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.phase = random.uniform(0, 2*3.141569)#randomise the starting phase
        self.image = game_objects.game.display.make_layer((int(self.max_radius*4),int(self.max_radius*4))).texture
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos

        self.shader = game_objects.shaders['circle']#draws a circle
        self.shader['size'] = self.image.size
        self.shader['gradient'] = 0.7#1 means gradient, 0 is without
        self.shader['color'] = self.colour
        self.update_size()

    def draw_shader(self):#his called just before the draw
        self.shader['radius'] = self.radius

    def update(self):
        super().update()
        self.update_size()

    def update_size(self):
        self.radius = self.max_radius*(math.sin(self.time + self.phase) + 1)

    def update_vel(self):
        self.velocity  = [0.5*math.sin(self.time + self.phase),-1]

class Fireflies(Circles):
    animations = {}
    def __init__(self,game_objects, parallax):
        super().__init__(game_objects, parallax)
        self.phase = random.randint(0, 360)#randomise the starting phase
        self.shader['radius'] = self.radius

    def set_parameters(self):
        self.colour = [153,153,0,150]#circle colour
        self.radius = 3*self.parallax[0]#particle radius, depends on parallax

    def update_vel(self):
        self.velocity  = [math.cos(self.animation.frame*0.01+self.phase),math.sin(self.animation.frame*0.01+self.phase)]

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
        for state in self.sprites.keys():
            for frame,image in enumerate(self.sprites[state]):
                img_copy = pygame.transform.scale(image,size)
                arr = pygame.PixelArray(img_copy)#make it an pixel arrat since it has a replace color function
                arr.replace(replace_color,new_colour)
                self.sprites[state][frame] = arr.make_surface()
                arr.close()

class Sakura(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.load_sprites_dict('Sprites/animations/weather/leaf'+str(rand)+'/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colours=[(255,192,203),(240,128,128),(255,182,193),(221,160,221),(219,112,147)]
        colour=colours[random.randint(0, len(colours)-1)]
        self.set_color(colour)

class Autumn(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites=Read_files.load_sprites_dict('Sprites/animations/weather/leaf'+str(rand)+'/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.true_pos

        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        colour=colors[random.randint(0, len(colors)-1)]
        self.set_color(colour)

class Snow(Weather_particles):
    def __init__(self,game_objects,parallax):
        super().__init__(game_objects,parallax)
        rand=random.randint(1,1)
        self.sprites = Read_files.load_sprites_dict('Sprites/animations/weather/snow/', game_objects)
        self.image = self.sprites['idle'][0]
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
        self.sprites=Read_files.load_sprites_dict('Sprites/animations/weather/rain/',game_objects)
        self.image = self.sprites['idle'][0]
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
