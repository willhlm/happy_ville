import pygame, sys
from gameplay.ui import ui_loader
from .base.base_ui import BaseUI

class OptionMenu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = OptionMenu.menu_ui
        self.image = self.menu_ui.sprites['idle'][0]
        self.current_button = 0
        self.update_arrow()

    def pool(game_objects):
        OptionMenu.menu_ui = getattr(ui_loader, 'OptionMenu')(game_objects)

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.display.render(self.image, self.game.screen_manager.screen)

        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)   

        #blit arrow
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
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
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.menu_ui.arrows[0].pressed()
                self.update_options()

    def update_options(self):
        if self.current_button == 0:#resolution
            self.game.state_manager.enter_state('Option_menu_display', category = 'menu')
        elif self.current_button == 1:#sounds
            self.game.state_manager.enter_state('Option_menu_sounds', category = 'menu')
        if self.current_button == 2:
            self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
        elif self.current_button == 3:
            self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

