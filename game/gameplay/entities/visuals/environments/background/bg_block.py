from gameplay.entities.base.static_entity import StaticEntity
from engine.utils import functions

class BgBlock(StaticEntity):
    def __init__(self, pos, game_objects, img, parallax, live_blur = False):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layers = None  # Initialize layer to None
        self.image = self.game_objects.game.display.surface_to_texture(img)
        self.rect[2] = self.image.width
        self.rect[3] = self.image.height
        
        if not live_blur:   
            blur_radius = functions.blur_radius(parallax)
            self.blur(blur_radius)#if we do not want live blur

    def blur(self, blur_radius):
        return
        if self.parallax[0] != 1:  # Don't blur if there is no parallax
            shader = self.game_objects.shaders['blur']
            shader['blurRadius'] = blur_radius  # Set the blur radius
            self.layers = self.game_objects.game.display.make_layer(self.image.size)# Make an empty layer
            self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline
            self.game_objects.game.display.render(self.image, self.layers, shader = shader)  # Render the image onto the layer
            self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
            self.image.release()
            self.image = self.layers.texture  # Get the texture of the layer

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos)  # Shader render

    def release_texture(self):  # Called when .kill() and when emptying the group
        self.image.release()
        if self.layers:  # Release layer if it exists, used for thre blurring
            self.layers.release()

