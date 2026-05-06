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
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#TODO
        self.background = self.game.display.make_layer(self.game.window_size)#TODO

        self.clean_slate()
        self.conv = self.speaker.dialogue.start_conversation()
        self.fade_alpha = self.game.game_objects.fade.create("alpha", 10, min_value=0, max_value=230)
        self.fade_mask = self.game.game_objects.fade.create("mask", 10, min_value=0, max_value=230, mask_kind="horizontal", feather=0.03)
        self.sign = 1#fade in and back

        if not self.conv:
            self.fade_back()

    def clean_slate(self):
        self.letter_frame = 0

    def update(self, dt):
        super().update(dt)
        self.letter_frame += self.print_frame_rate*dt
        self.fade_mask.step_linear(dt, self.sign * 5)
        self.fade_alpha.step_linear(dt, self.sign * 5)
        if self.fade_alpha.is_below(10):
            self.game.state_manager.exit_state()

    def render(self):
        super().render()
        self.conv_screen.clear(0, 0, 0, 0)#needed to make the self.background semi trasnaprant
        self.background.clear(10,10,10,100)#needed to make the self.background semi trasnaprant

        self.game.game_objects.font.render_text_bg(
            self.conv_screen,
            self.text_window_size,
            position=self.blit_pos,
        )
        
        if self.conv:
            self.game.game_objects.font.render(
                self.conv_screen,
                self.conv,
                letter_frame=int(self.letter_frame),
                color=(255,255,255,255),
                position=(180, self.blit_pos[1] + 20),
                width=272,
            )
        self.speaker.render_potrait(self.conv_screen)#some conversation target may not have potraits


        self.fade_alpha.render(
            self.background.texture,
            self.game.screen_manager.screen,
        )

        self.fade_mask.render(
            self.conv_screen.texture,
            self.game.screen_manager.screen,
        )

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

    def on_pop(self):
        self.conv_screen.release()
        if self.completed:            
            self.speaker.on_conversation_complete()
        else:
            self.speaker.on_conversation_cancelled()
