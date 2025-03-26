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
        """
        Updates the position of the layer based on the camera, ensuring pixel-perfect rendering.
        """
        # Compute integer camera position (prevents wobbling)
        camera_x = int(self.game.game_objects.camera_manager.camera.scroll[0] * self.parallax[0])
        camera_y = int(self.game.game_objects.camera_manager.camera.scroll[1] * self.parallax[1])

        # Compute fractional offset
        frac_x = (self.game.game_objects.camera_manager.camera.scroll[0] * self.parallax[0]) - camera_x
        frac_y = (self.game.game_objects.camera_manager.camera.scroll[1] * self.parallax[1]) - camera_y

        self.offset = (-frac_x, -frac_y)  # Store fractional offset for rendering

    def render(self, target):
        """
        Blits this layer onto the main screen with sub-pixel correction.
        """
        self.game.display.render(self.layer.texture, target, position = self.offset, shader = self.game.game_objects.shaders['pp'])

    def clear(self):
        """ Clears the layer (useful before drawing new frame). """
        self.layer.clear((0, 0, 0, 0))  # Fill with transparent

