import pygame
from gameplay.entities.interactables.base.interactables import Interactables

class Zoom_col(Interactables):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()
        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 1)
        self.center = kwarg.get('center', (0.5, 0.5))
        self.blur_timer = C.fps

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()

    def player_collision(self, player):
        self.blur_timer -= 1#dt
        if self.blur_timer < 0:
            player.shader_state.handle_input('blur')
            for group in self.game_objects.all_bgs.group_dict.keys():
                for sprite in self.game_objects.all_bgs.group_dict[group]:
                    if sprite.parallax[0] > 0.8:
                        sprite.blur_radius += (1.1/sprite.parallax[0] - sprite.blur_radius) * 0.06
                        sprite.blur_radius = min(1.1/ sprite.parallax[0], sprite.blur_radius)
                    else:
                        sprite.blur_radius -= (sprite.blur_radius - 0.2) * 0.06
                        sprite.blur_radius = max(sprite.blur_radius, 0.2)

        if self.interacted: return
        self.game_objects.camera_manager.zoom(rate = self.rate, scale = self.scale, center = self.center)
        self.interacted = True#sets to false when player gos away

    def player_noncollision(self):#when player doesn't collide: for grass
        self.blur_timer = C.fps
        self.interacted = False
        if self.game_objects.post_process.shaders.get('zoom', False):
            self.game_objects.post_process.shaders['zoom'].method = 'zoom_out'
            self.game_objects.player.shader_state.handle_input('idle')
            for group in self.game_objects.all_bgs.group_dict.keys():
                for sprite in self.game_objects.all_bgs.group_dict[group]:
                    if sprite.parallax[0] == 1: sprite.blur_radius = 0.2
                    else: sprite.blur_radius = min(1/sprite.parallax[0], 10)#limit the blur raidus for performance

