from engine.render.post_process import PostProcessLayer

class ScreenManager():
    def __init__(self, game):
        self.game = game
        self.screens = {}
        self.active_screens = []  # Which screens are currently in use
        
        self.screen_copy = self.game.display.make_layer(self.game.window_size)#used to get a copy of the screen: mostly for shaders
        self.screen = self.game.display.make_layer(self.game.window_size)#the screen we can use to render things on
        self.composite_screen = self.game.display.make_layer(self.game.display_size)#display size: need to be large to do the pp camera
        
        game.game_objects.signals.subscribe("layer_trigger_in", self.append_shader)
        game.game_objects.signals.subscribe("layer_trigger_update", self.update_layer_trigger)
        game.game_objects.signals.subscribe("layer_trigger_out", self.remove_shader)

    def register_screen(self, key, parallax):#called from maploader when loading each layer in titled
        if self.screens.get(key):#already exist, just update parallax
            self.screens[key].reset(parallax)
        else:
            self.screens[key] = ScreenLayer(self.game, parallax)
        self.activate_screen(key)     

        if key == 'bg1':
            if not self.screens.get('player'):#first time we load bg1, we also create the player screen
                self.screens['player'] = ScreenLayerPlayer(self.game)                
                self.screens['player_fg'] = ScreenLayer(self.game)#make a layer for player foreground, but in bg1
            self.activate_screen('player')
            self.activate_screen('player_fg')   
        
    def activate_screen(self, key):
        self.active_screens.append(key)
        
    def deactivate_screen(self, key):
        self.active_screens.remove(key)
        
    def clear_screens(self):#called from map loader, loading a new map
        self.active_screens = []   
        self.clear_shaders()    

    def render(self):#render multiple screen, for each parallax, with pp precision
        self.game.display.use_premultiplied_alpha_mode()
        for key in self.active_screens:     
            self.screens[key].render(self.composite_screen)#render to composite screen with pp precision              
        self.game.display.use_standard_alpha_mode()

    def get_screen(self, layer = None, include = False):#get a copy of screen (not pixel perfect), up to a specific layer (name according to tiled), excluding the layer if include is false.
        self.screen_copy.clear(0, 0, 0, 0)
        self.game.display.use_premultiplied_alpha_mode()
        
        if layer:
            idx = self.active_screens.index(layer)           
            screens_to_get = self.active_screens[:idx + int(include)] #up to layer.
        else:
            screens_to_get = self.active_screens
    
        for key in screens_to_get:       
            screen = self.screens[key]
            self.game.display.render(screen.layer.texture, self.screen_copy)
        self.game.display.use_standard_alpha_mode()
        return self.screen_copy

    def clear(self):
        self.screen.clear(0,0,0,0)
        for screen in self.screens.values():
            screen.clear(0,0,0,0)

    def append_shader(self, shader, layers, **kwarg):#can append shaders to the screen (post process like stff)
        for key in layers:     
            self.screens[key].append_shader(shader, **kwarg)

    def clear_shaders(self):
        for key in self.screens.keys():
            self.screens[key].clear_shaders()

    def remove_shader(self, shader, layers, **kwarg):#remove single shader for specivied layers
        for key in layers:
            self.screens[key].remove_shader(shader)

    def update_layer_trigger(self, shader, layers, **kwarg):#dynamically update shader uniforms
        for key in layers:     
            self.screens[key].update_shader(shader, **kwarg)

class ScreenLayer():
    def __init__(self, game, parallax = [1, 1]):
        """
        Initialize a screen layer.

        :param game: The main game object (for accessing the screen).
        :param parallax: Tuple (x, y) defining how much this layer moves compared to the camera.
        """
        self.game = game
        self.parallax = parallax#(x, y) parallax factor
        self.layer = self.game.display.make_layer(self.game.window_size)#TODO
        self.offset = [0, 0]

        self.post_process = PostProcessLayer(game.game_objects, self)

    def calculate_offset(self):      
        camera_scroll_x = self.game.game_objects.camera_manager.camera.interp_scroll[0] * self.parallax[0]
        camera_scroll_y = self.game.game_objects.camera_manager.camera.interp_scroll[1] * self.parallax[1]
        
        # Use fractional scroll for smooth offset
        frac_x = camera_scroll_x - int(camera_scroll_x)
        frac_y = camera_scroll_y - int(camera_scroll_y)
        
        self.offset = (-frac_x, frac_y )#fractional paty of the scroll

    def apply_pp(self, input, target):
        """
        Render this layer onto the main screen with sub-pixel correction.
        """
        self.calculate_offset()
        self.game.game_objects.shaders['pp']['u_camera_offset'] = self.offset
        self.game.game_objects.shaders['pp']['u_scale'] = self.game.scale
        self.game.game_objects.shaders['pp']['u_screen_size'] = self.game.window_size

        self.game.display.render(input.texture, target, scale = self.game.scale, shader = self.game.game_objects.shaders['pp'])      

    def render(self, composite_target):
        self.post_process.apply(source_layer=self.layer,final_target=composite_target)

    def reset(self, parallax):  
        self.parallax = parallax
        self.offset = [0, 0]

    def __getattr__(self, attr):
        return getattr(self.layer, attr)

    def append_shader(self, shader, **kwarg):        
        self.post_process.append_shader(shader, **kwarg)

    def update_shader(self, shader_name, **kwarg):#to dynamically update uniforms
        self.post_process.shaders[shader_name].set_uniforms(**kwarg)

    def remove_shader(self, shader, **kwarg):        
        self.post_process.remove_shader(shader)

    def clear_shaders(self):
        self.post_process.clear_shaders()

class ScreenLayerPlayer(ScreenLayer):
    def __init__(self, game):
        super().__init__(game, parallax = [1, 1])

    def calculate_offset(self):      
        camera_scroll_x = self.game.game_objects.player.blit_pos[0]
        camera_scroll_y = self.game.game_objects.player.blit_pos[1]
        
        # Use fractional scroll for smooth offset
        frac_x = camera_scroll_x - int(camera_scroll_x)
        frac_y = camera_scroll_y - int(camera_scroll_y)
        
        self.offset = (frac_x, -frac_y)#fractional paty of the scroll
