import pygame, math, random
import read_files
from entities import Animatedentity

class ScreenParticles(pygame.sprite.Sprite):#make a layer on screen, then use shaders to generate stuff. Better performance
    def __init__(self, game_objects, parallax, number_particles):
        super().__init__()
        size = 5
        width = int(game_objects.game.window_size[0] + 2*size)#size of the canvas
        height = int(game_objects.game.window_size[1] + 2*size)#size of the canvas
        self.image = game_objects.game.display.make_layer((width, height))

        self.game_objects = game_objects
        self.parallax = parallax
        self.time = 0
        self.number_particles = number_particles#max 20, hard coded in shader
        self.set_parameters()        

    def update(self):
        self.time += self.game_objects.game.dt
        self.update_partciles()

    def draw(self, target):
        self.game_objects.game.display.render(self.image.texture, target, shader = self.shader)#shader render

    def release_texture(self):
        self.image.release()           

    def set_parameters(self):#set stuff specific for the particles
        pass        

    def update_partciles(self):
        for i in range(0, self.number_particles):
            self.update_vel(i)
            self.update_centers(i)
            self.update_size(i)

    def update_vel(self, i):#should they move?
        pass

    def update_centers(self, i):
        self.centers[i] = [self.centers[i][0] + self.game_objects.game.dt*self.velocity[i][0]*self.parallax[0], self.centers[i][1] - self.game_objects.game.dt*self.velocity[i][1]*self.parallax[1]]

    def update_size(self, i):#should they change size?
        pass

class Vertical_circles(ScreenParticles):
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
