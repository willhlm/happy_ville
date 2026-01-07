from engine.utils import read_files
from gameplay.ui.managers import ui_loader
from ..base.base_ui import BaseUI

class OptionSounds(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.game_settings = read_files.read_json('config/game_settings.json')
        self.current_button = 0     
        self.sounds = ['overall', 'SFX', 'music']#the order in titled
        self.previous_button = None
        self._update_arrow()   

    def pool(game_objects):
        OptionSounds.menu_ui = getattr(ui_loader, 'OptionSounds')(game_objects)

    def update_render(self, dt):
        self.game.game_objects.ui.uis['menu'].update_time(dt)
        self.menu_ui.buttons[self.current_button].active()
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth
        
        # Update slider volumes to match current audio settings
        self._update_sliders()

    def _update_sliders(self):
        """Update all sliders to match current volume settings"""
        for i, slider in enumerate(self.menu_ui.slider):
            volume = self.game.game_objects.sound.audio_manager.volume_settings[self.sounds[i]]
            slider.set_volume(volume)

    def _update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect[0], button.rect.centery, button.rect[2], button.rect[3]

        for arrow in self.menu_ui.arrows:
            y_pos = by - arrow.rect.height * 0.5
            x_pos = self.menu_ui.results[self.current_button][0]
            if arrow.flip:
                arrow.set_pos((20 + x_pos, y_pos))  # +10 px padding
            else:# left arrow, align to left edge of button
                arrow.set_pos((bx - arrow.rect.width - 10 , y_pos))  # -10 px padding
        arrow.play_SFX()

    def _get_option_display_text(self, button_index):
        """Get the current value text for each option"""
        if button_index == 0:  # Resolution
            res = self.resolutions[self.resolution_index]
            return f"{res[0]}x{res[1]}"        
        elif button_index == 1:  # VSync
            return "ON" if self.game_settings['display']['vsync'] else "OFF"
        elif button_index == 2:  # Fullscreen
            return "ON" if self.game_settings['display']['fullscreen'] else "OFF"
        elif button_index == 3:  # fps
            res = self.fps[self.fps_index]
            return f"{res}"             
        return ""

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.game_objects.ui.uis['menu'].render_background(self.game.screen_manager.screen)

        #blit buttons
        for i, b in enumerate(self.menu_ui.buttons):
            b.render(self.game.screen_manager.screen)
            value_text = self.game.game_objects.sound.audio_manager.volume_settings[self.sounds[i]]                                        
            self.game.display.render_text(self.game.game_objects.font.font_atals,self.game.screen_manager.screen,str(value_text),letter_frame=1000,color=[255, 255, 255, 255],position=self.menu_ui.results[i])


        for b in self.menu_ui.slider:
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

    def on_exit(self):
        super().on_exit()
        self.game_settings['sounds'] = self.game.game_objects.sound.audio_manager.volume_settings
        read_files.write_json(self.game_settings, 'config/game_settings.json')#overwrite

    def handle_events(self, input):        
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self._update_arrow()
            self._update_button()  # Handle button state change
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self._update_arrow()
            self._update_button()  # Handle button state change

        elif event[2]['l_stick'][0] > 0 or (event[-1] == 'dpad_right' and event[0]):  # Right                        
            self.update_options(1)            
            
        elif event[2]['l_stick'][0] < 0 or (event[-1] == 'dpad_left' and event[0]):  # Left
            self.update_options(-1)

        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()

    def update_options(self, direction):
        """Cycle through option values (left/right)"""        
        if self.current_button == 0: #overall            
            self.game.game_objects.sound.change_volume('overall', direction)            
        elif self.current_button == 1:  # SFX
            self.game.game_objects.sound.change_volume('SFX', direction)            
        elif self.current_button == 2:  # music
            self.game.game_objects.sound.change_volume('music', direction)
        
        # Update playing sounds immediately
        self.game.game_objects.sound.sound_player.update_all_volumes()
        
        self.play_click_sound()

    def play_click_sound(self):
        for arrow in self.menu_ui.arrows:
            arrow.play_SFX()