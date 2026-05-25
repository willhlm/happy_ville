import pygame

class StaticEntity(pygame.sprite.Sprite):#all enteties
    def __init__(self, pos, game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)
        self.true_pos = list(self.rect.topleft)

        self.always_active = False#for the acivation manager, if it shuold alsoways update,redner or if it shoud be stopped while outside the screen
        self.shader = None#which shader program to run
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: needed when rendering the direction

    def update_render(self, dt):
        pass

    def update(self, dt):
        pass

    def draw(self, target):#called just before draw in group
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

    def release_texture(self):#called when emptying groups / deferred map cleanup
        pass

    def on_kill_cleanup(self):#called immediately when the entity is killed
        pass

    def kill(self):
        self.on_kill_cleanup()
        self.game_objects.lights.remove_owner_lights(self)
        self.game_objects.deferred_textures.track(self)
        super().kill()
