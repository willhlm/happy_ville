class ScreenManager():
    def __init__(self, game):
        self.game = game
        self.screens = {}
        self.active_screens = []  # Which screens are currently in use
        
        self.screen_copy = self.game.display.make_layer(self.game.window_size)#used to get a copy of the screen: mostly for shaders
        self.screen = self.game.display.make_layer(self.game.window_size)#the screen we can use to render things on
        self.composite_screen = self.game.display.make_layer(self.game.display._screen_res)#display size
        
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

    def render(self):#render multiple screen, for each parallax, with pp precision
        self.game.display.set_premultiplied_alpha_blending()
        for key in self.active_screens:     
            screen = self.screens[key]
            screen.update()#get the offset
            self.game.game_objects.shaders['pp']['u_camera_offset'] = screen.offset
            self.game.game_objects.shaders['pp']['u_scale'] = self.game.scale
            self.game.game_objects.shaders['pp']['u_screen_size'] = self.game.window_size
            self.game.display.render(screen.layer.texture, self.composite_screen, scale = self.game.scale, shader = self.game.game_objects.shaders['pp'])        
        self.game.display.set_normal_alpha_blending()

    def get_screen(self, layer = None, include = False):#get a copy of screen (not pixel perfect), up to a specific layer (name according to tiled), excluding the layer if include is false.
        self.screen_copy.clear(0, 0, 0, 0)
        self.game.display.set_premultiplied_alpha_blending()
        
        if layer:
            idx = self.active_screens.index(layer)           
            screens_to_get = self.active_screens[:idx + int(include)] #up to layer.
        else:
            screens_to_get = self.active_screens
    
        for key in screens_to_get:       
            screen = self.screens[key]
            self.game.display.render(screen.layer.texture, self.screen_copy)
        self.game.display.set_normal_alpha_blending()
        return self.screen_copy

    def clear(self):
        self.screen.clear(0,0,0,0)
        for screen in self.screens.values():
            screen.clear(0,0,0,0)

class ScreenLayer():
    def __init__(self, game, parallax = [1, 1]):
        """
        Initialize a screen layer.

        :param game: The main game object (for accessing the screen).
        :param parallax: Tuple (x, y) defining how much this layer moves compared to the camera.
        """
        self.game = game
        self.parallax = parallax#(x, y) parallax factor
        self.layer = self.game.display.make_layer(self.game.window_size)
        self.offset = [0,0]

    def update(self):      
        camera_scroll_x = self.game.game_objects.camera_manager.camera.interp_scroll[0] * self.parallax[0]
        camera_scroll_y = self.game.game_objects.camera_manager.camera.interp_scroll[1] * self.parallax[1]
        
        # Use fractional scroll for smooth offset
        frac_x = camera_scroll_x - int(camera_scroll_x)
        frac_y = camera_scroll_y - int(camera_scroll_y)
        
        self.offset = (-frac_x, frac_y )#fractional paty of the scroll

    def render(self, target, scale):
        """
        Blits this layer onto the main screen with sub-pixel correction.
        """
        self.game.game_objects.shaders['pp']['u_camera_offset'] = self.offset 
        self.game.game_objects.shaders['pp']['u_scale'] = scale 
        self.game.game_objects.shaders['pp']['u_screen_size'] = self.game.window_size
        self.game.display.render(self.layer.texture, target, scale = scale, shader = self.game.game_objects.shaders['pp'])#shader render  

    def reset(self, parallax):
        self.parallax = parallax
        self.offset = [0,0]

    def __getattr__(self, attr):
        return getattr(self.layer, attr)

class ScreenLayerPlayer(ScreenLayer):
    def __init__(self, game):
        super().__init__(game, parallax = [1, 1])

    def update(self):      
        camera_scroll_x = self.game.game_objects.player.blit_pos2[0]
        camera_scroll_y = self.game.game_objects.player.blit_pos2[1]
        
        # Use fractional scroll for smooth offset
        frac_x = camera_scroll_x - int(camera_scroll_x)
        frac_y = camera_scroll_y - int(camera_scroll_y)
        
        self.offset = (frac_x, -frac_y )#fractional paty of the scroll
