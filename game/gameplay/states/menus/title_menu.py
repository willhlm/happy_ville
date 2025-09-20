import pygame, sys
from gameplay.ui.managers import ui_loader
from .base.base_ui import BaseUI

class TitleMenu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = getattr(ui_loader, 'TitleMenu')(game.game_objects)
        self.play_music()
        self.image = self.menu_ui.sprites['idle'][0]
        self.current_button = 0
        self.update_arrow()

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def fade_update(self, dt):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.update_render(dt)

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.menu_ui.buttons[self.current_button].hoover()
        self.game.display.render(self.image, self.game.screen_manager.screen)#shader render

        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        #blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)        

        self.game.render_display(self.game.screen_manager.screen.texture)

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0 or (event[-1] == 'dpad_up' and event[0]):#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0 or (event[-1] == 'dpad_down' and event[0]):#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] in ('return', 'a'):
                self.menu_ui.buttons[self.current_button].pressed()#if we want to make it e.g. glow or something
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def play_music(self):
        self.channel = self.game.game_objects.sound.play_priority_sound(self.menu_ui.sounds['main'][0], index = 0, loop = -1, fade = 700, vol = 0.3)
        self.channel = self.game.game_objects.sound.play_priority_sound(self.menu_ui.sounds['whisper'][0], index = 1, loop = -1, fade = 700, vol = 0.1)

    def change_state(self):
        if self.current_button == 0:#new game
            self.menu_ui.arrows[0].pressed('new')#if we want to make it e.g. glow or something
            self.game.state_manager.enter_state('gameplay')

            #load new game level
            #self.game.game_objects.load_map(self,'village_1','1')
            #self.game.game_objects.load_map(self,'wakeup_forest_1','1')
            #self.game.game_objects.load_map(self,'crystal_mines_1','1')
            #self.game.game_objects.load_map(self,'nordveden_1','1')
            self.game.game_objects.load_map(self,'dark_forest_1','1')
            #self.game.game_objects.load_map(self,'tall_trees_1','1')
            #self.game.game_objects.load_map(self,'hlifblom_43','1')
            #self.game.game_objects.load_map(self,'rhoutta_encounter_3','1')
            #self.game.game_objects.load_map(self,'golden_fields_2','1')
            #self.game.game_objects.load_map(self,'collision_map_4','1')

        elif self.current_button == 1:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('load_menu')

        elif self.current_button == 2:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('option_menu')

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

