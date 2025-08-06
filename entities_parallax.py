import pygame, random, math
import entities
import read_files
from states import states_wind_objects, states_droplet_source, states_weather_particles, states_blur, states_shader

class Layered_objects(entities.Animatedentity):#objects in tiled that goes to different layers
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects)
        self.pause_group = game_objects.layer_pause
        self.group = game_objects.all_bgs.group_dict[layer_name]
        self.parallax = parallax
        self.layer_name = layer_name

        self.live_blur = live_blur
        self.blurtstate = states_blur.Idle(self) 

    def update(self, dt):
        super().update(dt)
        self.group_distance()

    def init_sprites(self, path):#save in memory. key (0,0) is reserved for none blurred images
        if self.live_blur:
            cache_key = (0,0)
            self.blurtstate = states_blur.Blur(self)
        else:
            cache_key = tuple(self.parallax)
        
        if type(self).animations.get(cache_key, False):#Check if sprites are already in memory
            self.sprites = type(self).animations[cache_key]
        else:# first time loading            
            self.sprites = read_files.load_sprites_dict(path, self.game_objects)
            type(self).animations[cache_key] = self.sprites
            
            if not self.live_blur and self.parallax[0] != 1:# Apply blur if not live and not parllax = 1
                self.blur()                    

    def blur(self):#
        shader = self.game_objects.shaders['blur']
        shader['blurRadius'] = 1/self.parallax[0]
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):     
                self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline           
                empty_layer = self.game_objects.game.display.make_layer(self.sprites['idle'][0].size)#need to be inside the loop to make new layers for each frame
                self.game_objects.game.display.render(self.sprites[state][frame], empty_layer, shader = shader)
                self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
                self.sprites[state][frame] = empty_layer.texture    

    def draw(self, target):
        self.blurtstate.set_uniform()#sets the blur radius
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.true_scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.true_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render      

    def release_texture(self):  # Called when .kill() and when emptying the group        
        pass  

    def group_distance(self):
        blit_pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.true_scroll[0], self.true_pos[1]-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        if blit_pos[0] < self.bounds[0] or blit_pos[0] > self.bounds[1] or blit_pos[1] < self.bounds[2] or blit_pos[1] > self.bounds[3]:
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause         

class Trees(Layered_objects):
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.currentstate = states_wind_objects.Idle(self)#

    def create_leaves(self,number_particles = 3):#should we have colour as an argument?
        for i in range(0,number_particles):
            obj = Leaves(self.spawn_box[0],self.game_objects,self.parallax,self.spawn_box[1],self.layer_name)
            self.game_objects.all_bgs.add(self.layer_name, obj)       

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

#light forest
class Tree_1(Trees):
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):        
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)                
        self.init_sprites('Sprites/animations/trees/tree_1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        
        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

class Tree_2(Trees):
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.init_sprites('Sprites/animations/trees/tree_2/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

class Cocoon(Layered_objects):#larv cocoon in light forest
    animations = {}
    def __init__(self, pos, game_objects,parallax, live_blur = False):
        super().__init__(pos, game_objects,parallax, live_blur)
        self.init_sprites('Sprites/animations/cocoon/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

class Vines_1(Layered_objects):#light forest
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)
        self.init_sprites('Sprites/animations/vines/vines_1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.true_pos = self.rect.topleft
        self.shader = game_objects.shaders['sway_wind']
        self.time = 0
        self.offset = random.uniform(0,10)
        self.upsidedown = 1

    def update(self):
        self.time += self.game_objects.game.dt
        self.group_distance()

    def draw(self,target):
        self.shader['TIME'] = self.time
        self.shader['offset'] = self.offset
        self.shader['upsidedown'] = self.upsidedown
        super().draw(target)

class Small_tree1(Layered_objects):
    animations = {}
    def __init__(self, pos, game_objects,parallax, live_blur = False):
        super().__init__(pos, game_objects,parallax, live_blur)
        self.init_sprites('Sprites/animations/bushes/small_tree1/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.time = 0

        self.shader = game_objects.shaders['sway_wind']
        self.offset = random.uniform(0,10)

    def update(self):
        self.time += self.game_objects.game.dt
        self.group_distance()

    def draw(self,target):
        self.shader['TIME'] = self.time
        self.shader['offset'] = self.offset
        self.shader['upsidedown'] = 0
        super().draw(target)

#lightf forest cave
class Ljusmaskar(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax, live_blur = False):
        super().__init__(pos,game_objects,parallax, live_blur)
        self.init_sprites('Sprites/animations/ljusmaskar/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

class Cave_grass(Layered_objects):
    animations = {}    
    def __init__(self,pos,game_objects,parallax, live_blur = False):
        super().__init__(pos,game_objects,parallax, live_blur)
        self.init_sprites('Sprites/animations/bushes/cave_grass/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

class Droplet_source(Layered_objects):
    animations = {}    
    def __init__(self,pos,game_objects,parallax, group, live_blur = False):
        super().__init__(pos,game_objects,parallax, live_blur)
        self.init_sprites('Sprites/animations/droplet/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.droplet = Droplet
        self.currentstate = states_droplet_source.Idle(self)
        self.group = group#all_bgs or all_fgs
    
        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
        else:
            self.shader_state = states_shader.Idle(self)

    def drop(self):#called from states                
        if self.parallax == [1,1]:#TODO need to check for bg and fg etc if fg should not go into eprojectiles?
            obj = entities.Droplet(self.rect.topleft, self.game_objects)       
            self.game_objects.eprojectiles.add(obj)
        else:#TODO need to put in all_bgs or all_gfs
            sprites = self.group.sprites()
            bg = self.group.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            obj = Droplet(self.rect.topleft, self.game_objects, self.parallax)       
            self.group.spritedict[obj] = self.group._init_rect#in add internal
            self.group._spritelayers[obj] = 0
            self.group._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.group)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)

class Falling_rock_source(Layered_objects):
    animations = {}    
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)
        self.init_sprites('Sprites/animations/falling_rock/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.currentstate = states_droplet_source.Idle(self)

    def drop(self):#called from states
        if self.parallax == [1,1]:#TODO need to check for bg and fg etc. I guess fg should not go into eprojectiles
            obj = entities.Falling_rock(self.rect.bottomleft, self.game_objects)
            self.game_objects.eprojectiles.add(obj)
        else:#TODO need to put in all_bgs or all_gfs
            sprites = self.game_objects.all_bgs.sprites()
            bg = self.game_objects.all_bgs.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            obj = Falling_rock(self.rect.topleft, self.game_objects, self.parallax)
            self.game_objects.all_bgs.spritedict[obj] = self.game_objects.all_bgs._init_rect#in add internal
            self.game_objects.all_bgs._spritelayers[obj] = 0
            self.game_objects.all_bgs._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.game_objects.all_bgs)

class Vines_2(Layered_objects):#light forest cave
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)
        self.init_sprites('Sprites/animations/vines/vines_2/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.true_pos = self.rect.topleft
        self.shader = game_objects.shaders['sway_wind']
        self.time = 0
        self.offset = random.uniform(0,10)
        self.upsidedown = 1

    def update(self):
        self.time += self.game_objects.game.dt
        self.group_distance()

    def draw(self,target):
        self.shader['TIME'] = self.time
        self.shader['offset'] = self.offset
        self.shader['upsidedown'] = self.upsidedown
        super().draw(target)

#crystal mines
class Crystals(Layered_objects):
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)  
        self.init_sprites('Sprites/animations/crystals/' + type(self).__name__.lower() + '/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.shader = game_objects.shaders['highlight']  
        
        self.speed = 2
        self.shine_progress = 0

    def update(self):
        super().update()  
        if self.shine_progress * self.speed >= 1:
            if random.randint(0,500) == 0: self.shine_progress = 0                    
        else:
            self.shine_progress += 0.01 * self.game_objects.game.dt

    def draw(self, target):
        self.shader['shine_progress'] = self.shine_progress
        self.shader['speed'] = self.speed
        super().draw(target)

class Crystal_1(Crystals):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)        

class Crystal_2(Crystals):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)  

class Crystal_3(Crystals):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)  

class Crystal_4(Crystals):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)  

class Crystal_5(Crystals):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)                          

#village
class Thor_mtn(Layered_objects):
    animations = {}
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)
        self.init_sprites('Sprites/animations/bg_animations/thor_mtn_village/')#blur or lead from memory                    
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.blur_radius = 1/parallax[0]

#general
class Light_source(Layered_objects):#should we decrease alpha for large parallax?
    def __init__(self, pos, game_objects, parallax, live_blur = False):
        super().__init__(pos, game_objects, parallax, live_blur)
        self.rect = pygame.Rect(pos[0],pos[1],16,16)
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()

    def update(self):
        self.group_distance()

    def draw(self, target):
        pass

#thigns that move in parallax
class Dynamic_layered_objects(Layered_objects):
    def __init__(self,pos,game_objects,parallax, layer_name, live_blur = False):
        super().__init__(pos,game_objects,parallax, layer_name, live_blur)
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
        self.true_pos = [self.true_pos[0] + self.game_objects.game.dt * self.velocity[0]*self.parallax[0], self.true_pos[1] + self.game_objects.game.dt * self.velocity[1]*self.parallax[1]]
        self.rect.topleft = self.true_pos.copy()

    def boundary(self):
        pass

class Droplet(Dynamic_layered_objects):#cosmetic droplet   
    def __init__(self,pos,game_objects,parallax, live_blur = False):
        super().__init__(pos,game_objects,parallax, live_blur)
        self.sprites = Droplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)        
        self.lifetime = 100

        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
        else:
            self.shader_state = states_shader.Idle(self)              

    def update(self):
        super().update()
        self.update_vel()
        self.destroy()

    def destroy(self):
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def update_vel(self):
        self.velocity[1] += 1
        self.velocity[1] = min(7,self.velocity[1])

    def pool(game_objects):
        Droplet.sprites = read_files.load_sprites_dict('Sprites/animations/droplet/droplet/', game_objects)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)

class Leaves(Dynamic_layered_objects):#leaves from trees
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
        Leaves.sprites = read_files.load_sprites_dict('Sprites/animations/weather/leaf'+str(random.randint(1,1))+'/', game_objects)#randomly choose a leaf type

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        self.update_vel()
        self.colour[-1] -= self.game_objects.game.dt*0.2
        self.colour[-1] = max(self.colour[-1],0)

    def update_vel(self):
        self.velocity[0] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[0]  - self.friction[0]*self.velocity[0] + math.sin(self.time*0.1+self.phase)*self.parallax[0]*0.3)
        self.velocity[1] += self.game_objects.game.dt*(self.game_objects.weather.wind.velocity[1] * self.friction[1] - self.friction[1]*self.velocity[1])

    def boundary(self):
        if self.colour[-1] < 5 or self.true_pos[1]-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1] > self.game_objects.game.window_size[1]+50:
            self.resetting()

    def reset(self):
        self.colour[-1] = random.uniform(255*self.parallax[0],255)
        self.velocity[1] = random.uniform(0.2,0.5)
        self.time = 0
        self.true_pos = [self.init_pos[0] + random.uniform(-self.spawn_size[0]*0.5, self.spawn_size[0]*0.5), self.init_pos[1] + random.uniform(-self.spawn_size[1]*0.5,self.spawn_size[1]*0.5)]
        self.rect.topleft = self.true_pos.copy()

class Falling_rock(Dynamic_layered_objects):
    def __init__(self,pos,game_objects,parallax, live_blur = False):
        super().__init__(pos,game_objects,parallax, live_blur)
        self.sprites = Falling_rock.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.lifetime = 100

    def update(self):
        super().update()
        self.update_vel()
        self.destroy()

    def destroy(self):
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def update_vel(self):
        self.velocity[1] += 1
        self.velocity[1] = min(7,self.velocity[1])

    def pool(game_objects):#save the texture in memory for later use
        Falling_rock.sprites = read_files.load_sprites_dict('Sprites/animations/falling_rock/rock/', game_objects)