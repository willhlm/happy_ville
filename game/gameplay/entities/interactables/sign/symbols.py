import pygame
from gameplay.entities.base.static_entity import StaticEntity

class Symbols(StaticEntity):#a part of sign, it blits the landsmarks in the appropriate directions
    def __init__(self, entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.game_objects = entity.game_objects
        self.image = self.game_objects.game.display.make_layer(entity.game_objects.game.window_size)#TODO
        self.rect = pygame.Rect(0, 0, self.image.texture.width, self.image.texture.height)
        self.rect.center = [entity.game_objects.game.window_size[0]*0.5,entity.game_objects.game.window_size[0]*0.5-100]
        self.image.clear(0,0,0,255)

        dir = {'left':[self.image.texture.width*0.25,150],'up':[self.image.texture.width*0.5,50],'right':[self.image.texture.width*0.75,150],'down':[self.image.texture.width*0.5,300]}
        for key in entity.directions.keys():
            self.game_objects.font.render(
                self.image,
                entity.directions[key],
                color=(255,255,255,255),
                position=dir[key],
                width=30,
            )

        self.render_fade = [self.render_in, self.render_out]
        self.init()

    def init(self):
        self.fade = self.game_objects.fade.create("alpha", 0, max_value=200)
        self.page = 0

    def update(self, dt):
        self.render_fade[self.page](dt)

    def draw(self, target):
        self.fade.render(self.image.texture, target)

    def render_in(self, dt):
        self.fade.step(dt)

    def render_out(self, dt):
        self.fade.step(-dt)

        if self.fade.is_below(10):
            self.init()
            self.kill()

    def finish(self):#called when fading out should start
        self.page = 1

    def release_texture(self):
        pass
