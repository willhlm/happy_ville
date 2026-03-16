import pygame
from .hud_meters import HudMeters
from .hud_widgets import HudWidgets

class HUD():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.blur_screen = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.offset = 5
        self.meters = HudMeters(self.game_objects, offset=self.offset)
        self.widgets = HudWidgets(self.game_objects)

    def update(self, dt):
        self.meters.update(dt)
        self.widgets.update(dt)

        self.update_overlay(dt)

    def update_overlay(self, dt):
        self.game_objects.ui.overlay.update(dt)

    def draw(self, composite_screen):
        self.blur_screen.clear(0,0,0,0)
        self.screen.clear(0,0,0,0)
        self.meters.draw(self.blur_screen)

        self.game_objects.shaders['blur_outline']['blurRadius'] = 1
        self.game_objects.game.display.render(self.blur_screen.texture, self.screen, shader = self.game_objects.shaders['blur_outline'])
        self.widgets.draw(self.screen)
        self.render_fps()#render on scren, witout blur             
        self.render_overlay(self.screen)        
        self.game_objects.game.display.render(self.screen.texture, composite_screen, scale = self.game_objects.game.scale)         

    def render_overlay(self, target):
        self.game_objects.game.display.use_premultiplied_alpha_mode()   
        self.game_objects.ui.overlay.draw(target)
        self.game_objects.game.display.use_standard_alpha_mode()

    def render_fps(self):
        if self.game_objects.game.RENDER_FPS_FLAG:
            fps_string = str(int(self.game_objects.game.game_loop.clock.get_fps()))
            text = 'fps ' + fps_string
            self.game_objects.game.display.render_text(self.game_objects.font.font_atals, self.screen, text, letter_frame = None, color = (255,255,255,255), position = (self.screen.width - 50, 10))
