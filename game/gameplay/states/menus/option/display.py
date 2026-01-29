from engine.utils import read_files
from gameplay.ui.loaders import OptionDisplayLoader
from ..base.base_ui import BaseUI

class OptionDisplay(BaseUI):
    def __init__(self, game):
        super().__init__(game)
        self.game_settings = read_files.read_json('config/game_settings.json')
        
        self.current_button = 0
        self.previous_button = None
        
        # Available resolutions
        self.resolutions = [(640, 360), (800, 450)]
        self.fps = [30, 60, 120]
        
        # Find current resolution index
        current_res = tuple(self.game_settings['display']['resolution'])
        current_fps = self.game_settings['display']['fps']
        self.resolution_index = self.resolutions.index(current_res)
        self.fps_index = self.fps.index(current_fps)
        
        self._update_arrow()
        self._update_button()

    def pool(game_objects):
        OptionDisplay.menu_ui = OptionDisplayLoader(game_objects)

    def _update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for index, arrow in enumerate(self.menu_ui.arrows):
            pos_x = self.menu_ui.results[index][0]
            if arrow.flip:  
                arrow.set_pos((pos_x + bw + 10, by))
            else:
                arrow.set_pos((bx - arrow.rect.width - 10, by))
        self.play_click_sound()

    def _update_button(self):
        """Handle button state transitions"""
        if self.previous_button is not None and self.previous_button != self.current_button:
            self.menu_ui.buttons[self.previous_button].on_exit()
        
        if self.previous_button != self.current_button:
            self.menu_ui.buttons[self.current_button].on_enter()
        
        self.previous_button = self.current_button

    def update_render(self, dt):
        """Called every frame"""
        self.game.game_objects.ui.uis['menu'].update_time(dt)
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)
        
        # Update active button animation
        self.menu_ui.buttons[self.current_button].active()

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
        self.game.screen_manager.screen.clear(0, 0, 0, 0)        
        self.game.game_objects.ui.uis['menu'].render_background(self.game.screen_manager.screen)

        # Render buttons with their current values
        for i, button in enumerate(self.menu_ui.buttons):
            button.render(self.game.screen_manager.screen)
            
            # Render the current option value to the right of the button
            value_text = self._get_option_display_text(i)
                                            
            self.game.display.render_text(self.game.game_objects.font.font_atals,self.game.screen_manager.screen,value_text,letter_frame=1000,color=[255, 255, 255, 255],position=self.menu_ui.results[i])

        # Render arrows
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position=arrow.true_pos, flip=arrow.flip)

        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        
        # Vertical navigation
        if event[2]['l_stick'][1] < 0 or (event[-1] == 'dpad_up' and event[0]):  # Up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self._update_arrow()
            self._update_button()
            
        elif event[2]['l_stick'][1] > 0 or (event[-1] == 'dpad_down' and event[0]):  # Down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self._update_arrow()
            self._update_button()
        
        # Horizontal cycling (left/right to change values)
        elif event[2]['l_stick'][0] > 0 or (event[-1] == 'dpad_right' and event[0]):  # Right
            self.cycle_option(1)
            
        elif event[2]['l_stick'][0] < 0 or (event[-1] == 'dpad_left' and event[0]):  # Left
            self.cycle_option(-1)
        
        # Actions
        elif event[0]:
            if event[-1] == 'start' or event[-1] == 'b':
                self.game.state_manager.exit_state()

    def cycle_option(self, direction):
        """Cycle through option values (left/right)"""
        if self.current_button == 0:  # Resolution
            self.resolution_index += direction
            # Wrap around
            if self.resolution_index < 0:
                self.resolution_index = len(self.resolutions) - 1
            elif self.resolution_index >= len(self.resolutions):
                self.resolution_index = 0
            
            # Update settings
            self.game_settings['display']['resolution'] = list(self.resolutions[self.resolution_index])

        elif self.current_button == 1:  # VSync
            self.game_settings['display']['vsync'] = not self.game_settings['display']['vsync']
            
        elif self.current_button == 2:  # Fullscreen
            self.game_settings['display']['fullscreen'] = not self.game_settings['display']['fullscreen']

        elif self.current_button == 3:  # fps
            self.fps_index += direction
            # Wrap around
            if self.fps_index < 0:
                self.fps_index = len(self.fps) - 1
            elif self.fps_index >= len(self.fps):
                self.fps_index = 0
            
            # Update settings
            self.game_settings['display']['fps'] = self.fps[self.fps_index]

        self.play_click_sound()

    def on_exit(self):
        super().on_exit()
        read_files.write_json(self.game_settings, 'config/game_settings.json')

    def play_click_sound(self):
        for arrow in self.menu_ui.arrows:
            arrow.play_SFX() 