from engine.utils import read_files
from gameplay.entities.shared.states import states_blur
from gameplay.entities.base.animated_entity import AnimatedEntity
from engine.utils import functions

class LayeredObjects(AnimatedEntity):#objects in tiled that goes to different layers
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects)
        self.pause_group = game_objects.layer_pause
        groups = game_objects.all_fgs if layer_name.startswith("fg") else game_objects.all_bgs
        self.group = groups.group_dict[layer_name]
        self.parallax = parallax
        self.layer_name = layer_name
        self.live_blur = live_blur

    def update(self, dt):
        super().update(dt)

    def init_sprites(self, path):#save in memory. key (0,0) is reserved for none blurred images
        self.game_objects.map_resources.register(type(self), type(self).release_animation_cache)
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

    @classmethod
    def release_animation_cache(cls):
        """Release this visual class's shared animation cache at map teardown."""
        released = set()
        for sprites_by_state in cls.animations.values():
            for frames in sprites_by_state.values():
                for texture in frames:
                    texture_id = id(texture)
                    if texture_id not in released:
                        texture.release()
                        released.add(texture_id)
        cls.animations.clear()

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))               
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render      

    def release_texture(self):  # Called when .kill() and when emptying the group        
        pass
