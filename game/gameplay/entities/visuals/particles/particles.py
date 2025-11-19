import pygame, math, random
from engine.system import animation
from engine.utils import read_files
from . import states_particles

class Particles(pygame.sprite.Sprite):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__()
        self.game_objects = game_objects
        self.spawn_point = [pos[0],pos[1]]

        self.angle_dist = kwarg.get('angle_dist', None)
        self.lifetime = kwarg.get('lifetime', 60)
        self.angle_spread = kwarg.get('angle_spread', [30, 30])
        self.colour = list(kwarg.get('colour', [255, 255, 255, 255]))#make a copy of the list by list()
        self.fade_scale = kwarg.get('fade_scale', 1)
        dir = kwarg.get('dir', 'isotropic')
        angle = self.define_angle(dir)

        distance = kwarg.get('distance', 0)
        vel = kwarg.get('vel', {'linear':[7,15]})

        self.angle = -(2*math.pi*angle)/360
        self.true_pos = [pos[0]+distance*math.cos(self.angle),pos[1]+distance*math.sin(self.angle)]
        motion = list(vel.keys())[0]#linear, wave, gravity motion etc
        self.set_velocity = {'linear':self.linear,'wave':self.wave, 'gravity':self.gravity, 'ejac':self.ejac}[motion]
        self.gravity_scale = kwarg.get('gravity_scale', 1)
        amp = random.uniform(min(vel[motion][0],vel[motion][1]), max(vel[motion][0],vel[motion][1]))
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]
        self.phase = random.uniform(-math.pi,math.pi)#for the cave grass relsease particles

        state = kwarg.get('state', 'Idle')
        self.currentstate = getattr(states_particles, state)(self)

    def update(self, dt):
        pass

    def update_render(self, dt):
        self.update_pos(dt)
        self.lifetime -= dt
        self.currentstate.update_render(dt)

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*dt, self.true_pos[1] + self.velocity[1]*dt]
        self.rect.center = self.true_pos
        self.hitbox.center = self.true_pos

    def gravity(self, dt):
        self.velocity[1] += dt *  self.gravity_scale

    def wave(self, dt):
        self.velocity  = [0.5*math.sin(self.lifetime*0.1 + self.angle + self.phase),-self.gravity_scale]

    def linear(self, dt):
        self.velocity[0] -= 0.01*self.velocity[0]*dt#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]*dt#0.1*math.sin(self.angle)

    def ejac(self, dt):
        end_y_vel = -0.9
        self.velocity[0] -= 0.065*self.velocity[0]*dt + 0.03*math.sin(self.phase)#0.1*math.cos(self.angle)
        #self.velocity[1] += self.game_objects.game.dt * self.gravity_scale * (end_y_vel-self.velocity[1])*0.1
        self.velocity[1] += dt * (end_y_vel-self.velocity[1])*0.1

    def fading(self, dt):
        self.colour[-1] -= self.fade_scale * dt
        self.colour[-1] = max(self.colour[-1], 0)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def define_angle(self,dir):#is there a better way?
        if dir == 'isotropic':
            angle = random.randint(-180, 180)#the ejection anglex
        elif isinstance(dir, (int, float)):#interger/float
            dir += 180 * random.randint(0,1)
            spawn_angle = 30
            angle = random.randint(dir - spawn_angle, dir + spawn_angle)#the ejection anglex
        elif self.angle_dist == 'normal':
            if dir[1] == -1:#hit from down hit
                spawn_angle = 30
                angle = random.randint(90-spawn_angle, 90+spawn_angle)#the ejection anglex
            elif dir[1] == 1:#hit from above hit
                spawn_angle = 30
                angle = random.randint(270-spawn_angle, 270+spawn_angle)#the ejection anglex
            elif dir[0] == -1:#rigth hit
                m = 0 + (self.angle_spread[1] - self.angle_spread[0])/2
                s = (self.angle_spread[1] + self.angle_spread[0])/2
                angle = random.normalvariate(mu = m, sigma=s)
            elif dir[0] == 1:#left hit
                m = 180 + (self.angle_spread[0] - self.angle_spread[1])/2
                s = (self.angle_spread[0] + self.angle_spread[1])/2
                angle = random.normalvariate(mu = m, sigma=s)
        
        else:#list
            if dir[1] == -1:#hit from down hit
                spawn_angle = 30
                angle = random.randint(90-spawn_angle, 90+spawn_angle)#the ejection anglex
            elif dir[1] == 1:#hit from above hit
                spawn_angle = 30
                angle = random.randint(270-spawn_angle, 270+spawn_angle)#the ejection anglex
            elif dir[0] == -1:#rigth hit
                angle = random.randrange(0-self.angle_spread[0], 0+self.angle_spread[1])#the ejection anglex
            elif dir[0] == 1:#left hit
                angle = random.randrange(180-self.angle_spread[1], 180+self.angle_spread[0])#the ejection anglex
            else:
                if dir[0] == 0:
                    angle = 90
                else:
                    angle = math.tan(dir[1]/dir[0])#just to avoid error
        return angle

    def draw(self, target):
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render

    def release_texture(self):
        pass

#shader particles: use a shader to draw them
class Circle(Particles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        scale = kwarg.get('scale',3)
        self.radius = random.randint(max(scale-1,1), round(scale+1))
        self.fade_scale =  kwarg.get('fade_scale',2)#how fast alpha should do down in self.fading()
        self.image = Circle.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()

        self.shader = game_objects.shaders['circle']#draws a circle
        self.gradient = kwarg.get('gradient', 0)#one means gradient, 0 is without

    def draw(self, target):#his called just before the draw
        self.shader['color'] = self.colour
        self.shader['radius'] = self.radius
        self.shader['gradient'] = self.gradient
        self.shader['size'] = self.image.size
        super().draw(target)

    def pool(game_objects):#save the stuff in memory for later use
        Circle.image = game_objects.game.display.make_layer((50,50)).texture

class Goop(Particles):#circles that "distorts" due to noise
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.empty = Goop.image2
        self.noise_layer = Goop.image3
        self.circle = Goop.image4
        self.fade_scale = 0

        self.game_objects.shaders['circle']['color'] = kwarg.get('colour',[1,1,1,1])
        self.game_objects.shaders['circle']['radius'] = 6
        self.game_objects.shaders['circle']['size'] = [50,50]
        self.game_objects.shaders['circle']['gradient'] = kwarg.get('gradient',0)#one means gradient, 0 is without
        self.game_objects.game.display.render(self.empty.texture, self.circle, shader=self.game_objects.shaders['circle'])#make perlin noise texture

        self.image = self.circle.texture
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()

        self.shader = self.game_objects.shaders['goop']
        self.time = 0

    def update(self, dt):
        super().update(dt)
        self.time += 0.01*dt

    def draw(self, target):#his called just before the draw
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.image.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = self.game_objects.camera_manager.camera.scroll
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]#"standard"
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['goop']['TIME'] = self.time
        self.game_objects.shaders['goop']['flowMap'] = self.noise_layer.texture
        super().draw(target)

    def pool(game_objects):#save the stuff in memory for later use
        Goop.image2 = game_objects.game.display.make_layer((50,50))
        Goop.image3 = game_objects.game.display.make_layer((50,50))
        Goop.image4 = game_objects.game.display.make_layer((50,50))

class Spark(Particles):#a general one
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.fade_scale =  kwarg.get('fade_scale', 1)#how fast alpha should do down in self.fading()

        self.image = Spark.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()

        self.shader = game_objects.shaders['spark']
        self.shader['size'] = self.image.size
        self.shader['scale'] = kwarg.get('scale', 1)

    def draw(self, target):#called from group draw
        self.shader['colour'] = self.colour
        self.shader['velocity'] = self.velocity
        super().draw(target)

    def pool(game_objects):#save the stuff in memory for later use
        Spark.image = game_objects.game.display.make_layer((50,50)).texture

#texture particles: use a texture as a reference
class FloatyParticles(Particles):#particles with a texture
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.animation = animation.Animation(self, framerate = 0.7)
        self.sprites = FloatyParticles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = self.game_objects.shaders['particles_configure']

        random_value = random.uniform(0.7,1)
        self.colour1 = (0,0.5*random_value,1*random_value,1)#main colour
        self.colour2 = (1,1,1,1)#seond
        self.colour3 = (1,0,0,1)#third9        

    def update(self, dt):
        self.animation.update(dt)
        self.update_pos(dt)
        self.update_velocity(dt)

    def update_uniforms(self):
        self.shader['colour1'] = self.colour1
        self.shader['colour2'] = self.colour2
        self.shader['colour3'] = self.colour3
        self.shader['normalised_frame'] = self.animation.frame/len(self.sprites['idle'])

    def draw(self, target):#his called just before the draw
        self.update_uniforms()
        super().draw(target)

    def reset_timer(self):#when animation is finished
        self.kill()

    def update_velocity(self, dt):
        self.velocity[1] += dt*0.01

    def pool(game_objects):#save the stuff in memory for later use
        FloatyParticles.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/cosmetics/particles/floaty/', game_objects)

class Offset(Particles):#not implemented fully -> need angular motion
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Offset.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = self.game_objects.shaders['particles_configure']

        random_value = random.uniform(0.7,1)
        self.colour1 = (0,0.5*random_value,1*random_value,1)#main colour
        self.colour2 = (1,1,1,1)#seond
        self.colour3 = (1,0,0,1)#third9

        self.time = 0

    def update(self, dt):
        self.update_pos(dt)
        self.update_velocity()
        self.destroy()
        self.time += dt
        self.lifetime -= dt

    def update_uniforms(self):
        self.shader['colour1'] = self.colour1
        self.shader['colour2'] = self.colour2
        self.shader['colour3'] = self.colour3
        self.shader['normalised_frame'] = self.animation.frame/len(self.sprites['idle'])

    def draw(self, target):#his called just before the draw
        self.update_uniforms()
        super().draw(target)

    def update_velocity(self):
        self.velocity  = [math.sin(self.time*0.1),math.sin(self.time*0.1)-0.5]

    def pool(game_objects):#save the stuff in memory for later use
        Offset.sprites = read_files.load_sprites_dict('Sprites/GFX/particles/offset/', game_objects)
