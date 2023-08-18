import pygame
from Entities import Animatedentity
import Read_files
import states_wind_objects, states_droplet
from weather import Leaves#move leaves here?

class Layered_objects(Animatedentity):#objects in tiled that goes to different layers
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects)
        self.pause_group = game_objects.layer_pause
        self.group = game_objects.all_bgs
        self.parallax = parallax

    def update(self):
        super().update()
        self.group_distance()

    def init_sprites(self):#Only blur if it is the first time loading the object. Otherwise, copy from memory
        try:#if it is not the first one
            self.sprites.sprite_dict =  type(self).animations[tuple(self.parallax)]
        except:#if it is the first tree loading, blur it:
            if self.parallax[0] != 1:#don't blur if oarallax = 1
                self.blur(self.game_objects.map.blur_value(self.parallax))
            type(self).animations[tuple(self.parallax)] = self.sprites.sprite_dict#save to memery for later use

    def blur(self,blur_value):#
        for state in self.sprites.sprite_dict.keys():
            for frame, image in enumerate(self.sprites.sprite_dict[state]):
                self.sprites.sprite_dict[state][frame] = pygame.transform.gaussian_blur(image, blur_value,repeat_edge_pixels=True)#box_blur

class Trees(Layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.currentstate = states_wind_objects.Idle(self)#

    def create_leaves(self,number_particles = 3):#should we have colour as an argument?
        for i in range(0,number_particles):
            obj = Leaves(self.game_objects,self.parallax,self.spawn_box)
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
        self.sprites = Read_files.Sprites_Player('Sprites/animations/trees/light_forest_tree1/')
        self.init_sprites()#blur or lead from memory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

class Light_forest_tree2(Trees):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/trees/light_forest_tree2/')
        self.init_sprites()#blur or lead from memory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

class Ljusmaskar(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/ljusmaskar/')
        self.init_sprites()#blur or lead from memory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def group_distance(self):
        pass

class Droplet(Layered_objects):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/droplet/droplet')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.true_pos = pos
        self.velocity = [0,0]
        self.lifetime = 100

    def group_distance(self):
        pass

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
        self.true_pos = [self.true_pos[0],self.true_pos[1] + self.velocity[1]]
        self.rect.topleft = self.true_pos.copy()

class Droplet_source(Layered_objects):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/droplet/source')
        self.init_sprites()#blur or lead from memory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.droplet = Droplet
        self.currentstate = states_droplet.Idle(self)

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
