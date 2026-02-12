import pygame, sys
from gameplay.ui.loaders import TitleMenuLoader
from .base.base_ui import BaseUI

class TitleMenu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = TitleMenuLoader(game.game_objects)
        self.play_music()
        self.game_title = self.menu_ui.sprites['title'][0]

        self.current_button = 0
        self.previous_button = None  # Track previous button
        self._update_arrow()
        self._update_button()  # Initialize first button as active

    def update_render(self, dt):
        self.menu_ui.buttons[self.current_button].active()# Always call active on the current button (for continuous hover effects)

        self.game.game_objects.ui.uis['menu'].update_time(dt)
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def fade_update(self, dt):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.update_render(dt)

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.game_objects.ui.uis['menu'].render_background(self.game.screen_manager.screen)
        self.game.display.render(self.game_title, self.game.screen_manager.screen)

        # Blit buttons
        for b in self.menu_ui.buttons:
            b.render(self.game.screen_manager.screen)

        # Blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)

        self.game.render_display(self.game.screen_manager.screen.texture)

    def _update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect[0], button.rect.centery, button.rect[2], button.rect[3]

        for arrow in self.menu_ui.arrows:
            y_pos = by - arrow.rect.height * 0.5
            if arrow.flip:
                arrow.set_pos((bx + bw + 10, y_pos))  # +10 px padding
            else:# left arrow, align to left edge of button
                arrow.set_pos((bx - arrow.rect.width - 10, y_pos))  # -10 px padding
        arrow.play_SFX()

    def _update_button(self):
        """Handle button state transitions when selection changes"""

        # Exit the previous button (if there was one)
        if self.previous_button is not None and self.previous_button != self.current_button:
            self.menu_ui.buttons[self.previous_button].on_exit()

        # Enter the new button (if it's different)
        if self.previous_button != self.current_button:
            self.menu_ui.buttons[self.current_button].on_enter()

        # Update previous button tracker
        self.previous_button = self.current_button

    def handle_events(self, input):
        event = input.output()
        input.processed()

        if event[2]['l_stick'][1] < 0 or (event[-1] == 'dpad_up' and event[0]):#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self._update_arrow()
            self._update_button()  # Handle button state change

        elif event[2]['l_stick'][1] > 0 or (event[-1] == 'dpad_down' and event[0]):#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self._update_arrow()
            self._update_button()  # Handle button state change

        elif event[0]:
            if event[-1] in ('return', 'a'):
                self.menu_ui.buttons[self.current_button].pressed()
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def play_music(self):
        self.channel = self.game.game_objects.sound.play_background_sound(self.menu_ui.sounds['main'][0], index = 0, loop = -1, fade = 700, volume = 0.3)
        self.channel = self.game.game_objects.sound.play_background_sound(self.menu_ui.sounds['whisper'][0], index = 1, loop = -1, fade = 700, volume = 0.1)

    def change_state(self):
        if self.current_button == 0:#new game
            self.menu_ui.arrows[0].pressed('new')#if we want to make it e.g. glow or something
            self.game.state_manager.enter_state('gameplay')                               
            #self.game.state_manager.enter_state('new_game')

            #load new game level
            #self.game.game_objects.map.load_map(self,'village_1','1')
            #self.game.game_objects.map.load_map(self,'wakeup_forest_0','1')
            #self.game.game_objects.map.load_map(self,'spirit_world_1','1')
            #self.game.game_objects.map.load_map(self,'crystal_mines_1','1')
            #self.game.game_objects.map.load_map(self,'village_5','1')
            #self.game.game_objects.map.load_map(self,'nordveden_windtest','1')
            #self.game.game_objects.map.load_map(self,'nordveden_1','1')
            self.game.game_objects.map.load_map(self,'tall_trees_1','1')
            #self.game.game_objects.map.load_map(self,'dark_forest_1','5')
            #self.game.game_objects.map.load_map(self,'hlifblom_1','1')
            #self.game.game_objects.map.load_map(self,'rhoutta_encounter_3','1')
            #self.game.game_objects.map.load_map(self,'golden_fields_2','1')
            #self.game.game_objects.map.load_map(self,'collision_map_4','1')

        elif self.current_button == 1:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('load_menu')

        elif self.current_button == 2:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('option_menu')

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()
