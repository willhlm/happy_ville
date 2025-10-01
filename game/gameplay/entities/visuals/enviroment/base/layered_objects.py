from engine.utils import read_files
from gameplay.entities.shared.states import states_blur
from gameplay.entities.base.animated_entity import AnimatedEntity
from engine.utils import functions

class LayeredObjects(AnimatedEntity):#objects in tiled that goes to different layers
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects)
        self.pause_group = game_objects.layer_pause
        self.group = game_objects.all_bgs.group_dict[layer_name]
        self.parallax = parallax
        self.layer_name = layer_name
        self.live_blur = live_blur

    def update(self, dt):
        super().update(dt)
        self.group_distance()

    def init_sprites(self, path):#save in memory. key (0,0) is reserved for none blurred images
        if self.live_blur:
            cache_key = (0,0)
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
        shader['blurRadius'] = functions.blur_radius(self.parallax)
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):     
                self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline           
                empty_layer = self.game_objects.game.display.make_layer(self.sprites['idle'][0].size)#need to be inside the loop to make new layers for each frame
                self.game_objects.game.display.render(self.sprites[state][frame], empty_layer, shader = shader)
                self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
                self.sprites[state][frame] = empty_layer.texture    

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))               
        self.game_objects.game.display.render(self.image, target, position = pos)#shader render      

    def release_texture(self):  # Called when .kill() and when emptying the group        
        pass  

    def group_distance(self):
        blit_pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.true_scroll[0], self.true_pos[1]-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        if blit_pos[0] < self.bounds[0] or blit_pos[0] > self.bounds[1] or blit_pos[1] < self.bounds[2] or blit_pos[1] > self.bounds[3]:
            self.remove(self.group)#self.group.remove_from_layer(self.layer_name, self)#remove from group
            self.add(self.pause_group)#add to pause        