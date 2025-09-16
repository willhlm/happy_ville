from . import states_wind_objects
from gameplay.entities.enviroment.base.layered_objects import LayeredObjects
from gameplay.entities.enviroment import Leaves

class BaseTree(LayeredObjects):
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