from gameplay.ui.loaders import OptionMenuLoader
from ..base.base_ui import BaseUI

class OptionMenu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = OptionMenu.menu_ui

        self.current_button = 0
        self.previous_button = None  # Track previous button
        self._update_arrow()
        self._update_button()  # Initialize first button as active

    def pool(game_objects):
        OptionMenu.menu_ui = OptionMenuLoader(game_objects)

    def _update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def update_render(self, dt):
        self.game.game_objects.ui.uis['menu'].update_time(dt)
        self.menu_ui.buttons[self.current_button].active()
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.game_objects.ui.uis['menu'].render_background(self.game.screen_manager.screen)

        #blit buttons
        for b in self.menu_ui.buttons:
            b.render(self.game.screen_manager.screen)

        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)   

        #blit arrow
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
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self._update_arrow()
            self._update_button()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self._update_arrow()
            self._update_button()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.menu_ui.arrows[0].pressed()
                self.update_options()

    def update_options(self):
        if self.current_button == 0:#resolution
            self.game.state_manager.enter_state('option_display')
        elif self.current_button == 1:#sounds
            self.game.state_manager.enter_state('option_sounds')
        if self.current_button == 2:
            self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
        elif self.current_button == 3:
            self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

    def on_exit(self):
        for b in self.menu_ui.buttons:
            b.on_exit()