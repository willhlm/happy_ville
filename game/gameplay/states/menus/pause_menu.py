import pygame, sys
from gameplay.ui.managers import ui_loader
from .base.base_ui import BaseUI

class PauseMenu(BaseUI):#when pressing ESC duing gameplay
    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = getattr(ui_loader, 'PauseMenu')(game.game_objects)
        self.current_button = 0
        self.update_arrow()

        self.image = self.game.display.make_layer(self.game.display_size)
        self.game.game_objects.shaders['blur']['blurRadius'] = 1
        self.game.display.render(self.game.screen_manager.composite_screen.texture, self.image, shader = self.game.game_objects.shaders['blur'])

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def render(self):
        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        #blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip) 
    
        self.game.render_display(self.image.texture, scale = False)
        self.game.render_display(self.game.screen_manager.screen.texture)        
     
    def handle_events(self, input):
        event = input.output()
        input.processed()
        if not input.key:#if it is a directinal input
            if event[2]['l_stick'][1] < 0:#up
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.menu_ui.buttons) - 1
                self.update_arrow()
            elif event[2]['l_stick'][1] > 0:#down
                self.current_button += 1
                if self.current_button >= len(self.menu_ui.buttons):
                    self.current_button = 0
                self.update_arrow()
        if event[0]:
            if event[-1] in ['a', 'return']:
                self.menu_ui.arrows[0].pressed()
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

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

