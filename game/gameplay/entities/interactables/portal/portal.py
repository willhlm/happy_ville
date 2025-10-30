from gameplay.entities.base.static_entity import StaticEntity
from . import states_portal

class Portal_2(StaticEntity):#same as portal but masked based. Doesnt work becasue the mask is repeated for some reason
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.mask_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 0.4#one is screen size

        self.state = kwarg.get('state', None)

        game_objects.interactables.add(Place_holder_interacatble(self, game_objects))#add a dummy interactable to the group, since portal cannot be in inetracatles
        game_objects.render_state.handle_input('portal', portal = self)

    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.bg_grey_layer.release()
        self.bg_distort_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self, dt):
        self.currentstate.update()#handles the radius and thickness of portal
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #mask
        self.game_objects.shaders['circle_pos']['radius'] = self.radius
        self.game_objects.shaders['circle_pos']['color'] = [255,255,255,255]
        self.game_objects.shaders['circle_pos']['gradient'] = 1
        self.game_objects.game.display.render(self.empty_layer.texture, self.mask_layer, shader = self.game_objects.shaders['circle_pos'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort_2']['TIME'] = self.time
        self.game_objects.shaders['distort_2']['maskTexture'] = self.mask_layer.texture
        self.game_objects.shaders['distort_2']['center'] = blit_pos
        self.game_objects.shaders['distort_2']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort_2']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort_2'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['distort_2'])#make them gre

class Portal(StaticEntity):#portal to make a small spirit world with challenge rooms
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 1#one is screen size

        self.state = kwarg.get('state', None)

        game_objects.interactables.add(Place_holder_interacatble(self, game_objects))#add a dummy interactable to the group, since portal cannot be in inetracatles
        game_objects.render_state.handle_input('portal', portal = self)

    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.bg_grey_layer.release()
        self.bg_distort_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self, dt):
        self.currentstate.update()#handles the radius and thickness of portal
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort']['TIME'] = self.time
        self.game_objects.shaders['distort']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['distort']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort']['center'] = [self.rect.center[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.center[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['distort']['radius'] = self.radius
        self.game_objects.shaders['distort']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.empty_layer, shader = self.game_objects.shaders['distort'])#make them grey
        self.game_objects.shaders['edge_light']['TIME'] = self.time
        self.game_objects.shaders['edge_light']['textureNoise'] = self.noise_layer.texture
        self.game_objects.game.display.render(self.empty_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['edge_light'])#make them grey