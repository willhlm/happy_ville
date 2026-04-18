from gameplay.states import Gameplay
from engine import constants as C

class Conversation(Gameplay):
    def __init__(self, game, speaker):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.velocity = [0,0]
        self.speaker = speaker
        self.completed = False
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (352, 96)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),50]
        self.background = self.game.display.make_layer(self.text_window_size)#TODO
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#TODO

        self.clean_slate()
        self.conv = self.speaker.dialogue.start_conversation()
        self.alpha = 10#alpha of the conversation screen
        self.sign = 1#fade in and back
        if not self.conv:
            self.fade_back()

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_window_size)
        self.game.display.render(self.text_window, self.background)#shader render

    def update(self, dt):
        super().update(dt)
        self.letter_frame += self.print_frame_rate*dt
        self.alpha += self.sign * dt * 5
        self.alpha = min(self.alpha,230)
        if self.alpha < 10:
            self.game.state_manager.exit_state()

    def render(self):
        super().render()
        self.conv_screen.clear(10,10,10,100)#needed to make the self.background semi trasnaprant

        self.game.display.render(self.background.texture, self.conv_screen, position = self.blit_pos)
        if self.conv:
            self.game.display.render_text(self.game.game_objects.font.font_atals, self.conv_screen, text = self.conv, letter_frame = int(self.letter_frame), color = (255,255,255,255), position = (180,self.blit_pos[1] + 20), width = 272)
        self.speaker.render_potrait(self.conv_screen)#some conversation target may not have potraits

        self.game.game_objects.shaders['alpha']['alpha'] = self.alpha
        self.game.display.render(self.conv_screen.texture, self.game.screen_manager.screen, shader = self.game.game_objects.shaders['alpha'])#shader render
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        input.processed()
        if input.pressed:#press
            if input.name == 'start':
                self.fade_back()

            elif input.name == 'y':
                if not self.conv:
                    self.fade_back()
                    return
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000

                else:#check if we have a series of conversations or not
                    conv = self.speaker.dialogue.advance_conversation()
                    if not conv:
                        self.completed = True
                        self.fade_back()
                    else:
                        self.clean_slate()
                        self.conv = conv

    def fade_back(self):
        self.sign = -1

    def on_exit(self):
        self.conv_screen.release()
        self.background.release()
        if self.completed:
            self.speaker.on_conversation_complete()
        else:
            self.speaker.on_conversation_cancelled()
