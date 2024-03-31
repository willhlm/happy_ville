import pygame, random, math
import Entities
import Read_files
import states_wind_objects, states_droplet, states_weather_particles

class Layered_objects(Entities.Animatedentity):#objects in tiled that goes to different layers
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects)
        self.pause_group = game_objects.layer_pause
        self.group = game_objects.all_bgs
        self.parallax = parallax

    def update(self):
        super().update()
        self.group_distance()

    def init_sprites(self, path):#Only blur if it is the first time loading the object. Otherwise, copy from memory
        if  type(self).animations.get(tuple(self.parallax), False):#not the firsy time
            images = type(self).animations[tuple(self.parallax)]
            self.sprites = images
        else:#first time loading
            self.sprites = Read_files.load_sprites_dict(path, self.game_objects)
            if self.parallax[0] != 1:#don't blur if parallax = 1
                self.blur()
            type(self).animations[tuple(self.parallax)] = self.sprites#save to memery for later use

    def blur(self):#
        shader = self.game_objects.shaders['blur']
        shader['blurRadius'] = 1/self.parallax[0]
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):
                empty_layer = self.game_objects.game.display.make_layer(self.sprites['idle'][0].size)#need to be inside the loop to make new layers for each frame
                self.game_objects.game.display.render(self.sprites[state][frame],empty_layer,shader = shader)
                self.sprites[state][frame] = empty_layer.texture

    def draw(self):
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = pos, shader = self.shader)#shader render

class Trees(Layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.currentstate = states_wind_objects.Idle(self)#

    def create_leaves(self,number_particles = 3):#should we have colour as an argument?
        for i in range(0,number_particles):
            obj = Leaves(self.spawn_box[0],self.game_objects,self.parallax,self.spawn_box[1])
            self.game_objects.all_bgs.add(obj)

    def blowing(self):#called when in wind state
        return
        sprites = self.game_objects.all_bgs.sprites()
        self.index = sprites.index(self)

        obj = Leaves(self.game_objects,self.parallax,[self.rect.center,[64,64]],kill = True)
        #manuall add to a specific layer
        self.game_objects.all_bgs.spritedict[obj] = self.game_objects.all_bgs._init_rect#in add internal
        self.game_objects.all_bgs._spritelayers[obj] = 0
        self.game_objects.all_bgs._spritelist.insert(self.index,obj)
        obj.add_internal(self.game_objects.all_bgs)

class Light_forest_tree1(Trees):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/trees/light_forest_tree1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

    def release_texture(self):
        pass

class Light_forest_tree2(Trees):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/trees/light_forest_tree2/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

    def release_texture(self):
        pass

class Ljusmaskar(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/ljusmaskar/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

    def group_distance(self):
        pass

    def release_texture(self):
        pass

class Cave_grass(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/bushes/cave_grass/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

    def group_distance(self):
        pass

    def release_texture(self):
        pass

class Cocoon(Layered_objects):#larv cocoon in light forest
    animations = {}
    def __init__(self, pos, game_objects,parallax):
        super().__init__(pos, game_objects,parallax)
        self.init_sprites('Sprites/animations/cocoon/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

    def release_texture(self):
        pass

class Droplet_source(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/droplet/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.droplet = Droplet
        self.currentstate = states_droplet.Idle(self)

    def release_texture(self):
        pass

    def group_distance(self):
        pass

    def drop(self):#called from states
        sprites = self.game_objects.all_bgs.sprites()
        bg = self.game_objects.all_bgs.reference[tuple(self.parallax)]
        index = sprites.index(bg)#find the index in which the static layer is located
        pos = self.rect.topleft
        obj = Droplet(pos,self.game_objects,self.parallax)
        self.game_objects.all_bgs.spritedict[obj] = self.game_objects.all_bgs._init_rect#in add internal
        self.game_objects.all_bgs._spritelayers[obj] = 0
        self.game_objects.all_bgs._spritelist.insert(index,obj)#it goes behind the static layer of reference
        obj.add_internal(self.game_objects.all_bgs)

class Falling_rock_source(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.init_sprites('Sprites/animations/falling_rock/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.currentstate = states_droplet.Idle(self)

    def release_texture(self):
        pass

    def group_distance(self):
        pass

    def drop(self):#called from states
        if self.parallax == [1,1]:
            obj = Entities.Falling_rock(self)
            self.game_objects.eprojectiles.add(obj)
        else:
            sprites = self.game_objects.all_bgs.sprites()
            bg = self.game_objects.all_bgs.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            pos = self.rect.topleft
            obj = Falling_rock(pos,self.game_objects,self.parallax)
            self.game_objects.all_bgs.spritedict[obj] = self.game_objects.all_bgs._init_rect#in add internal
            self.game_objects.all_bgs._spritelayers[obj] = 0
            self.game_objects.all_bgs._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.game_objects.all_bgs)

class Light_source(Layered_objects):#works for parallax = 1. Not sure how we would liek to deal with light sources for other parallax
    def __init__(self, pos, game_objects, parallax):
        super().__init__(pos, game_objects, parallax)
        self.rect = pygame.Rect(pos[0],pos[1],16,16)
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()

    def update(self):
        self.group_distance()

#thigns that move in parallax
class Dynamic_layered_objects(Layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.velocity = [0,0]
        self.friction = [0.5,0]
        self.true_pos = pos

    def group_distance(self):
        pass

    def update(self):
        super().update()
        self.update_pos()
        self.boundary()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.parallax[0], self.true_pos[1] + self.velocity[1]*self.parallax[1]]
        self.rect.topleft = self.true_pos.copy()

    def boundary(self):
        pass

class Droplet(Dynamic_layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.load_sprites_dict('Sprites/animations/droplet/droplet/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.lifetime = 100

    def update(self):
        super().update()
        self.update_vel()
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def update_vel(self):
        self.velocity[1] += 1
        self.velocity[1] = min(7,self.velocity[1])

class Leaves(Dynamic_layered_objects):#leaves from trees
    def __init__(self, pos, game_objects, parallax, size, kill = False):
        super().__init__(pos, game_objects,parallax)
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

    def release_texture(self):
        pass

    def draw(self):
        self.shader['colour'] = self.colour
        super().draw()

    def pool(game_objects):#save the texture in memory for later use
        Leaves.sprites = Read_files.load_sprites_dict('Sprites/animations/weather/leaf'+str(random.randint(1,1))+'/', game_objects)#randomly choose a leaf type

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        self.update_vel()
        self.colour[-1] -= self.game_objects.game.dt*0.2
        self.colour[-1] = max(self.colour[-1],0)

    def update_vel(self):
        self.velocity[0] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[0] - self.friction[0]*self.velocity[0] + math.sin(self.time*0.1+self.phase)*self.parallax[0]*0.3)
        self.velocity[1] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[1] - self.friction[1]*self.velocity[1])

    def boundary(self):
        if self.colour[-1] < 5 or self.true_pos[1]-self.parallax[1]*self.game_objects.camera.scroll[1] > self.game_objects.game.window_size[1]+50:
            self.resetting()

    def reset(self):
        self.colour[-1] = random.uniform(255*self.parallax[0],255)
        self.velocity[1] = random.uniform(0.2,0.5)
        self.time = 0
        self.true_pos = [self.init_pos[0] + random.uniform(-self.spawn_size[0]*0.5, self.spawn_size[0]*0.5), self.init_pos[1] + random.uniform(-self.spawn_size[1]*0.5,self.spawn_size[1]*0.5)]
        self.rect.topleft = self.true_pos.copy()

class Falling_rock(Dynamic_layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.load_sprites_dict('Sprites/animations/falling_rock/rock/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.lifetime = 100

    def update(self):
        super().update()
        self.update_vel()
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def update_vel(self):
        self.velocity[1] += 1
        self.velocity[1] = min(7,self.velocity[1])
