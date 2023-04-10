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

        self.layer_index = len(self.game_objects.all_bgs.sprites())

    def update_pos(self,scroll):
        self.true_pos = [self.true_pos[0] + self.parallax[0]*scroll[0], self.true_pos[1] + self.parallax[1]*scroll[1]]
        self.rect.bottomleft = self.true_pos.copy()

    def create_leaves(self,number_particles = 3):
        for i in range(0,number_particles):#slightly faster if we make the object once and copy it instead?
            obj = Leaves(self.game_objects,self.parallax,self.spawn_box)
            self.game_objects.all_bgs.add(obj)#need to add in proper layer group

    def blowing(self):#called when enter wind state: not working yet
        return
        for i in range(0,10):
            obj = Leaves(self.game_objects,self.parallax,[self.rect.center,[64,64]])
            obj._layer = self.layer_index
            self.game_objects.all_bgs.add(obj,layer = self.layer_index)#need to add to a specific layer...
