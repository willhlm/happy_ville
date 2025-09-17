from gameplay.entities.base.static_entity import StaticEntity
from gameplay.entities.shared.states import states_blur

class BgBlock(StaticEntity):
    def __init__(self, pos, game_objects, img, parallax, live_blur = False):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layers = None  # Initialize layer to None
        self.image = self.game_objects.game.display.surface_to_texture(img)
        self.rect[2] = self.image.width
        self.rect[3] = self.image.height

        if self.parallax[0] < 1:
            self.blur_radius = min(1/self.parallax[0], 10)#set a limit to 10. Bigger may cause performance issue
        else:
            self.blur_radius = min(1/self.parallax[0], 10)#set a limit to 10. Bigger may cause performance issue

        if not live_blur:
            self.blurstate = states_blur.Idle(self)
            self.blur()#if we do not want live blur
        else:#if live
            self.blurstate = states_blur.Blur(self)
            if self.parallax[0] == 1: self.blur_radius = 0.2#a small value so you don't see blur

    def blur(self):
        if self.parallax[0] != 1:  # Don't blur if there is no parallax
            shader = self.game_objects.shaders['blur']
            shader['blurRadius'] = self.blur_radius  # Set the blur radius
            self.layers = self.game_objects.game.display.make_layer(self.image.size)# Make an empty layer
            self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline
            self.game_objects.game.display.render(self.image, self.layers, shader = shader)  # Render the image onto the layer
            self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
            self.image.release()
            self.image = self.layers.texture  # Get the texture of the layer

    def draw(self, target):
        self.blurstate.set_uniform()#zsets the blur radius
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)  # Shader render

    def release_texture(self):  # Called when .kill() and when emptying the group
        self.image.release()
        if self.layers:  # Release layer if it exists, used for thre blurring
            self.layers.release()

