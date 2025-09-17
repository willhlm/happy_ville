from gameplay.states import Gameplay
from engine import constants as C

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.velocity = [0,0]
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (352, 96)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),50]
        self.background = self.game.display.make_layer(self.text_window_size)#TODO
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#TODO

        self.clean_slate()
        self.conv = self.npc.dialogue.get_conversation()
        self.alpha = 10#alpha of the conversation screen
        self.sign = 1#fade in and back

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

        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(self.background.texture, self.conv_screen, position = self.blit_pos)
        self.game.display.render(text, self.conv_screen, position = (180,self.blit_pos[1] + 20), shader = self.game.game_objects.shaders['colour'])#shader render
        self.npc.render_potrait(self.conv_screen)#some conversation target may not have potraits
        text.release()
        self.game.game_objects.shaders['alpha']['alpha'] = self.alpha

        self.game.display.render(self.conv_screen.texture, self.game.screen_manager.screen, shader = self.game.game_objects.shaders['alpha'])#shader render
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:
            if event[-1] == 'start':
                self.fade_back()

            elif event[-1] == 'y':
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000

                else:#check if we have a series of conversations or not
                    self.npc.dialogue.increase_conv_index()
                    conv = self.npc.dialogue.get_conversation()
                    if not conv:
                        self.fade_back()
                    else:
                        self.clean_slate()
                        self.conv = conv

    def fade_back(self):
        self.sign = -1

    def on_exit(self):
        self.conv_screen.release()
        self.background.release()
        self.npc.buisness()

