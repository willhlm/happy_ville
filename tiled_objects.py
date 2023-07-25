import pygame
from Entities import Animatedentity
import Read_files, states_wind_objects
from weather import Leaves

class Tree(Animatedentity):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects)
        self.currentstate = states_wind_objects.Idle(self)#
        self.pause_group = game_objects.layer_pause
        self.group = game_objects.all_bgs
        self.parallax = parallax

    def create_leaves(self,number_particles = 3):#should we have colour as an argument?
        for i in range(0,number_particles):#slightly faster if we make the object once and copy it instead?
            obj = Leaves(self.game_objects,self.parallax,self.spawn_box)
            self.game_objects.all_bgs.add(obj)

    def update(self):
        super().update()
        self.group_distance()

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

class Light_forest_tree1(Tree):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/tiled_objects/light_forest_tree1/')
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

class Light_forest_tree2(Tree):
    animations = {}
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects,parallax)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/tiled_objects/light_forest_tree2/')
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
