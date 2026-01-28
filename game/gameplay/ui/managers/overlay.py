import pygame, sys
from gameplay.ui.managers import ui_loader
from gameplay.ui.components import InventoryPointer

class BaseUI():
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects

    def update(self, dt):
        self.screen_alpha += dt*4
        self.screen_alpha = min(self.screen_alpha, 230)

    def render(self):
        pass

    def handle_events(self,input):
        input.processed()

    def on_exit(self, **kwarg):
        pass

    def on_enter(self, **kwarg):
        self.screen_alpha = kwarg.get('screen_alpha', 0)

    def blit_screen(self):#blits everything first to self.game_state.screen. Then blit it to the game screen at the end
        self.game_objects.shaders['alpha']['alpha'] = self.screen_alpha        
        self.game_objects.game.display.render(self.game_objects.ui.screen.texture, self.game_objects.game.screen_manager.screen, shader = self.game_objects.shaders['alpha'])
        self.game_objects.game.render_display(self.game_objects.game.screen_manager.screen.texture)

class Oerlay(BaseUI):#to render overlay Uis, like ability explanations
    def __init__(self, game_objects, image_name, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.overlay_UI = getattr(ui_loader, image_name)(game_objects)                        

    def update(self, dt):
        super().update(dt)
        pass

    def render(self):
        self.game_objects.ui.screen.clear(0, 0, 0, 0)#clear the screen
        self.blit_description()
        self.blit_bottons()
        self.blit_screen()

    def blit_description(self):
        pass

    def blit_bottons(self):
        for index, button in enumerate(self.overlay_UI.buttons.keys()):
            self.game_objects.game.display.render(self.iventory_UI.buttons[button].image, self.game_objects.ui.screen, position = self.iventory_UI.buttons[button].rect.topleft)#shader render
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(self.texts[index], self.game_objects.ui.screen, position = self.iventory_UI.buttons[button].rect.center,shader = self.game_objects.shaders['colour'])#shader render

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:#press
            elif event[-1]=='a' or event[-1]=='return':
                pass
 
 
