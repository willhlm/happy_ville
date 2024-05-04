import pygame, math, random, states_particles

class Particles(pygame.sprite.Sprite):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__()
        self.game_objects = game_objects
        self.spawn_point = [pos[0],pos[1]]

        self.lifetime = kwarg.get('lifetime', 60)
        self.colour = kwarg.get('colour', [255,255,255,255])
        dir = kwarg.get('dir', 'isotropic') 
        angle = self.define_angle(dir)

        distance = kwarg.get('distance', 400)
        vel = kwarg.get('vel', {'linear':[7,13]})
        
        self.angle = -(2*math.pi*angle)/360
        self.true_pos = [pos[0]+distance*math.cos(self.angle),pos[1]+distance*math.sin(self.angle)]
        motion = list(vel.keys())[0]#linear moetion or wave motion
        self.update_velocity = {'linear':self.linear,'wave':self.wave}[motion]
        amp = random.uniform(min(vel[motion][0],vel[motion][1]), max(vel[motion][0],vel[motion][1]))
        self.velocity = [-amp*math.cos(self.angle),-amp*math.sin(self.angle)]
        self.phase = random.uniform(-math.pi,math.pi)#for the cave grass relsease particles
        state = kwarg.get('state', 'Idle')
        self.state = getattr(states_particles, state)(self)

    def update(self):
        self.update_pos()
        self.lifetime -= self.game_objects.game.dt
        self.state.update()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.game_objects.game.dt, self.true_pos[1] + self.velocity[1]*self.game_objects.game.dt]
        self.rect.center = self.true_pos
        self.hitbox.center = self.true_pos

    def wave(self):
        self.velocity  = [0.5*math.sin(self.lifetime*0.1 + self.angle + self.phase),-1]

    def linear(self):
        self.velocity[0] -= 0.01*self.velocity[0]*self.game_objects.game.dt#0.1*math.cos(self.angle)
        self.velocity[1] -= 0.01*self.velocity[1]*self.game_objects.game.dt#0.1*math.sin(self.angle)

    def fading(self):
        self.colour[-1] -= self.fade_scale*self.game_objects.game.dt
        self.colour[-1] = max(self.colour[-1],0)

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def define_angle(self,dir):#is there a better way?
        if dir=='isotropic':
            angle=random.randint(-180, 180)#the ejection anglex
        elif dir == -1:#rigth hit
            spawn_angle = 30
            angle=random.randint(0-spawn_angle, 0+spawn_angle)#the ejection anglex
        elif dir == 1:#left hit
            spawn_angle = 30
            angle=random.randint(180-spawn_angle, 180+spawn_angle)#the ejection anglex
        else:#integer
            dir += 180*random.randint(0,1)
            spawn_angle = 10
            angle=random.randint(dir-spawn_angle, dir+spawn_angle)#the ejection anglex
        return angle

    def draw(self, target):
        pos = (int(self.rect[0]-self.game_objects.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render

    def release_texture(self):
        pass

class Circle(Particles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        scale = kwarg.get('scale',1)
        self.radius = random.randint(max(scale-1,1), round(scale+1))
        self.fade_scale = 0.1#how fast alpha should do down
        self.image = Circle.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()

        self.shader = game_objects.shaders['circle']#draws a circle
        self.shader['size'] = self.image.size
        self.shader['gradient'] = kwarg.get('gradient', 0)#one means gradient, 0 is without

    def draw(self, target):#his called just before the draw
        self.shader['color'] = self.colour
        self.shader['radius'] = self.radius
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

    def update(self):
        super().update()
        self.time += 0.01*self.game_objects.game.dt

    def draw(self, target):#his called just before the draw
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.image.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = self.game_objects.camera.scroll
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
        self.fade_scale = 0.4

        self.image = Spark.image
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()

        self.shader = game_objects.shaders['spark']
        self.shader['size'] = self.image.size
        self.shader['scale'] = kwarg.get('scale', 1)

    def draw(self, target):#called from group draw
        self.shader['colour'] = self.colour
        self.shader['velocity'] =self.velocity
        super().draw(target)

    def pool(game_objects):#save the stuff in memory for later use
        Spark.image = game_objects.game.display.make_layer((50,50)).texture
