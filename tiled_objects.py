import pygame
from Entities import Animatedentity
import Read_files, states_wind_objects
from weather import Leaves

class Light_forest_tree1(Animatedentity):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects)
        self.currentstate = states_wind_objects.Idle(self)#
        self.sprites = Read_files.Sprites_Player('Sprites/animations/tiled_objects/light_forest_tree1')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = self.rect.copy()
        self.true_pos = self.rect.bottomleft
        self.parallax = parallax

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

        self.convert_alpha()#a temporary solution

    def convert_alpha(self):#a temporary solution
        for state in self.sprites.sprite_dict.keys():
            for frame,image in enumerate(self.sprites.sprite_dict[state]):
                self.sprites.sprite_dict[state][frame] = image.convert_alpha()

    def blur(self,blur_value):#called from maploader
        for state in self.sprites.sprite_dict.keys():
            for frame, image in enumerate(self.sprites.sprite_dict[state]):
                self.sprites.sprite_dict[state][frame] = pygame.transform.gaussian_blur(image, blur_value,repeat_edge_pixels=True)#box_blur

    def update_pos(self,scroll):
        self.true_pos = [self.true_pos[0] + self.parallax[0]*scroll[0], self.true_pos[1] + self.parallax[1]*scroll[1]]
        self.rect.bottomleft = self.true_pos.copy()

    def create_leaves(self,number_particles = 3):
        for i in range(0,number_particles):#slightly faster if we make the object once and copy it instead?
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
