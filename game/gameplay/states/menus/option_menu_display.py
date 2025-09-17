import pygame, sys
from engine.utils import read_files
from gameplay.ui import ui_loader
from gameplay.ui.elements import MenuArrow
from .base.base_ui import BaseUI

class OptionMenuDisplay(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['vsync', 'fullscreen','resolution']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = MenuArrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update_arrow(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos((ref_pos[0] - 10, ref_pos[1]))
        self.arrow.play_SFX()

    def blit_buttons(self):
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.game.screen_manager.screen, position = self.button_rects[b].topleft)

            settig_string = self.game.game_objects.font.render((60,12), str(self.game_settings['display'][b]))
            self.game.game_objects.shaders['colour']['colour'] = (0,0,0,255)
            self.game.display.render(settig_string, self.game.screen_manager.screen, position = [self.button_rects[b].centerx + 50,self.button_rects[b].centery] ,shader = self.game.game_objects.shaders['colour'])#shader render
            settig_string.release()

    def render(self):
        #fill game.screen
        self.game.screen_manager.screen.clear(255,255,255, 255)

        #blit title
        self.game.display.render(self.title, self.game.screen_manager.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5, 50))

        #blit buttons
        self.blit_buttons()

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen_manager.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])
        self.game.render_display(self.game.screen_manager.screen.texture)
        #self.arrow.draw(self.game.screen)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options(1)
            elif event[-1] in ('b'):
                self.update_options(-1)

    def on_exit(self):
        super().on_exit()
        read_files.write_json(self.game_settings, 'game_settings.json')#overwrite

    def update_options(self, int):
        if self.current_button == 0:#vsync
            self.game_settings['display']['vsync'] = not self.game_settings['display']['vsync']
        if self.current_button == 1:#fullsceren
            self.game_settings['display']['fullscreen'] = not self.game_settings['display']['fullscreen']
        elif self.current_button == 2:#resolution
            pass

