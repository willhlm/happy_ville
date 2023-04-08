from Entities import Animatedentity
import Read_files
from weather import Leaves

class Light_forest_tree1(Animatedentity):
    def __init__(self,pos,game_objects,parallax):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/tiled_objects/light_forest_tree1')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = self.rect.copy()
        self.true_pos = self.rect.bottomleft
        self.parallax = parallax
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]#for leaves
        self.create_leaves()

    def update_pos(self,scroll):
        self.true_pos = [self.true_pos[0] + self.parallax[0]*scroll[0], self.true_pos[1] + self.parallax[1]*scroll[1]]
        self.rect.bottomleft = self.true_pos.copy()

    def create_leaves(self,number_particles = 10):
        for i in range(0,number_particles):#slightly faster if we make the object once and copy it instead
            obj = Leaves(self.game_objects,self.parallax,self.spawn_box)
            self.game_objects.all_bgs.add(obj)#nned to add in proper position group
