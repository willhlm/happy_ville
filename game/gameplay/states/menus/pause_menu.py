import pygame, sys
from gameplay.ui.loaders import PauseMenuLoader
from .base.base_ui import BaseUI

class PauseMenu(BaseUI):#when pressing ESC duing gameplay
    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = PauseMenuLoader(game.game_objects)

        self.image = self.game.display.make_layer(self.game.display_size)
        self.game.game_objects.shaders['blur']['blurRadius'] = 1
        self.game.display.render(self.game.screen_manager.composite_screen.texture, self.image, shader = self.game.game_objects.shaders['blur'])

        self.current_button = 0
        self.previous_button = None  # Track previous button
        self._update_arrow()
        self._update_button()  # Initialize first button as active

    def update_render(self, dt):
        self.menu_ui.buttons[self.current_button].active()# Always call active on the current button (for continuous hover effects)
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

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

    def render(self):
        self.game.screen_manager.screen.clear(50,50,50,150)
        
        #blit buttons
        for b in self.menu_ui.buttons:
            b.render(self.game.screen_manager.screen)

        #blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip) 
    
        self.game.render_display(self.image.texture, scale = False)
        self.game.render_display(self.game.screen_manager.screen.texture)  

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
                self.game.state_manager.exit_state()

    def change_state(self):
        if self.current_button == 0:
            self.game.state_manager.exit_state()

        elif self.current_button == 1:
            self.game.state_manager.enter_state('option_menu')

        elif self.current_button == 2:#exit to main menu
            for state in self.game.state_manager.state_stack[1:]:#except the first one
                state.release_texture()
            self.game.state_manager.state_stack = [self.game.state_manager.state_stack[0]]
            self.game.state_manager.state_stack[-1].play_music()

