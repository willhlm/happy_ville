class ScreenManager():
    def __init__(self, game):
        self.game = game
        self.screens = {}
        self.active_screens = []  # Which screens are currently in use
        self.screen = self.game.display.make_layer(self.game.window_size)#used to get a copy of the screen: mostly for shaders
        
    def register_screen(self, key, parallax):#called from maploader when loading each layer in titled
        if self.screens.get(key):#already exist, just update parallax
            self.screens[key].reset(parallax)
        else:
            self.screens[key] = ScreenLayer(self.game, parallax)
        self.activate_screen(key)
        
    def activate_screen(self, key):
        self.active_screens.append(key)
        self._sort_screens()
        
    def deactivate_screen(self, key):
        self.active_screens.remove(key)
        
    def clear_screens(self):#called from map loader, loading a new map
        self.active_screens = []       

    def _sort_screens(self):#Keep original order but move 'main' to the end
        if 'main' in self.active_screens:
            self.active_screens.remove('main')
            self.active_screens.append('main')

    def render(self):#render multiple screen, for each parallax, with pp precision
        self.game.display.set_premultiplied_alpha_blending()
        for key in self.active_screens:     
            screen = self.screens[key]
            screen.update()#get the offset
            self.game.game_objects.shaders['pp']['u_camera_offset'] = screen.offset
            self.game.game_objects.shaders['pp']['u_scale'] = self.game.scale
            self.game.game_objects.shaders['pp']['u_screen_size'] = self.game.window_size
            self.game.display.render(screen.layer.texture, self.game.display.screen, scale = self.game.scale, shader = self.game.game_objects.shaders['pp'])        
        self.game.display.set_normal_alpha_blending()

    def get_screen(self, layer = None):#ge ta copy of screen, up to a specific layer (name according to tiled). Doesn't copy things that are rendered on the main screen
        self.screen.clear(0, 0, 0, 0)
        self.game.display.set_premultiplied_alpha_blending()
        for key in self.active_screens:       
            screen = self.screens[key]
            self.game.display.render(screen.layer.texture, self.screen)
        self.game.display.set_normal_alpha_blending()
        return self.screen

class ScreenLayer():
    def __init__(self, game, parallax):
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
        camera_scroll_x = self.game.game_objects.camera_manager.camera.true_scroll[0] * self.parallax[0]
        camera_scroll_y = self.game.game_objects.camera_manager.camera.true_scroll[1] * self.parallax[1]
        
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