import pygame

from gameplay.entities.base.static_entity import StaticEntity
from . import states_portal

class Portal(StaticEntity):#portal to make a small spirit world with challenge rooms
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 1#one is screen size
        
    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.bg_grey_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self, dt):
        self.currentstate.update(dt)#handles the radius and thickness of portal
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.empty_layer.clear(0,0,0,0)
        self.noise_layer.clear(0,0,0,0)

        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = 'player_fg', include = True)

        self.game_objects.shaders['distort']['TIME'] = self.time
        self.game_objects.shaders['distort']['screen'] = screen_copy.texture
        self.game_objects.shaders['distort']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['distort']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort']['center'] = [self.rect.center[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.center[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['distort']['radius'] = self.radius
        self.game_objects.shaders['distort']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.empty_layer.texture, target, shader=self.game_objects.shaders['distort'])
