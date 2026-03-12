import pygame 
from gameplay.entities.projectiles.base.projectiles import Projectiles

class SlowmotionField(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)        
        self.temp_layer = SlowmotionField.temp_layer
        self.rect = pygame.Rect((0, 0), self.temp_layer.size)
        self.rect.center = pos
        self.true_pos = [float(self.rect.left), float(self.rect.top)]
        self.hitbox = self.rect.copy()

        self.progress = 0
        self.duration = kwarg.get('duration', 300)
        self.slow_scale = kwarg.get('slow_scale', 0.1)
        self.slow_duration = kwarg.get('slow_duration', 20)

    def pool(game_objects):
        size = (256, 256)
        SlowmotionField.temp_layer = game_objects.game.display.make_layer(size)

    def update(self, dt):
        pass

    def update_render(self, dt):
        self.progress += dt * 0.05
        self.progress = min(self.progress, 1)
        self.duration -= dt
        if self.duration <= 0:
            self.kill()

    def draw(self, target):
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = 'player', include = True)
        camera_scroll = self.game_objects.camera_manager.camera.interp_scroll

        position = [int(self.true_pos[0] - camera_scroll[0]), int(self.true_pos[1] - camera_scroll[1])]

        self.game_objects.shaders['slowmotion']['progress'] = self.progress
        self.game_objects.shaders['slowmotion']['resolution'] = self.rect.size
        self.game_objects.shaders['slowmotion']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['slowmotion']['section'] = [position[0], position[1], self.rect.width, self.rect.height]
        self.game_objects.shaders['slowmotion']['SCREEN_TEXTURE'] = screen_copy.texture

        self.game_objects.game.display.render(self.temp_layer.texture, target, position = position, shader=self.game_objects.shaders['slowmotion'])

    def release_texture(self):
        pass

    def apply_slow_motion(self, entity):
        hitstop = getattr(entity, 'hitstop', None)
        if hitstop is None: return            
        hitstop.start(duration=self.slow_duration, scale=self.slow_scale)

    #collisions
    def collision_platform(self, collision_plat):#collision platform   
        pass

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        pass

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        pass

    def collision_interactables(self, inetractable):#latest collision version
        pass

    def collision_interactables_fg(self,interactable):#2d water, 
        pass
