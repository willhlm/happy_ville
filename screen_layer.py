import pygame

class Screen_layer():
    def __init__(self, game, parallax = (1.0, 1.0)):
        """
        Initialize a screen layer.

        :param game: The main game object (for accessing the screen).
        :param parallax: Tuple (x, y) defining how much this layer moves compared to the camera.
        """
        self.game = game
        self.parallax = parallax  # (x, y) parallax factor
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

    def clear(self):
        """ Clears the layer (useful before drawing new frame). """
        self.layer.clear((0, 0, 0, 0))  # Fill with transparent

