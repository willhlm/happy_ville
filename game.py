import pygame, sys
import game_objects
import constants as C
import read_files
import state_manager
from pygame_render import RenderEngine

#pygame.print_debug_info()

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale = self.scale_size(2)#get the scale according to your display size
        display_size = [int(self.window_size[0] * self.scale), int(self.window_size[1] * self.scale)]
        game_settings = read_files.read_json('game_settings.json')['display']

        self.display = RenderEngine(display_size[0], display_size[1], fullscreen = game_settings['fullscreen'], vsync = game_settings['vsync'])
        self.screen = self.display.make_layer(self.window_size)

        #initiate game related values
        self.clock = pygame.time.Clock()
        self.fixed_dt = 1.0  # 60 physics updates per second
        self.accumulator = 0.0

        self.game_objects = game_objects.Game_Objects(self)
        self.state_manager = state_manager.State_manager(self, 'Title_menu')        

        #debug flags
        self.DEBUG_MODE = True
        self.RENDER_FPS_FLAG = True
        self.RENDER_HITBOX_FLAG = True
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN])
        pygame.event.set_blocked([pygame.TEXTINPUT])#for some reason, there is a text input here and there. So, blocking it

    def event_loop(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.game_objects.controller.map_inputs(event)#makes a list of inputs (input buffer)

        self.game_objects.controller.continuous_input_checks()#check every frame independent of event: right, left, up, down
        #self.state_stack[-1].continuous_input_checks()#tdiscrete_inputs_UI is inprinciple not needed for gameplay state
        inputs = self.game_objects.controller.input_buffer.copy()
        self.game_objects.input_interpreter.update(dt)#checks for flicks and other input related things
        for input in inputs:
            input.update(dt)
            self.state_manager.handle_events(input)

    def run(self):
        while True:
            self.screen.clear(0, 0, 0, 0)

            # Frame time
            frame_time = 60 * self.clock.tick(C.fps) * 0.001
  
            self.accumulator += frame_time

            # Handle events ONCE per frame
            self.event_loop(frame_time)

            while self.accumulator >= self.fixed_dt:
                self.state_manager.update(self.fixed_dt)
                self.accumulator -= self.fixed_dt

            self.state_manager.render()
            self.display.render(self.screen.texture, self.display.screen, scale=self.scale)
            pygame.display.flip()

    def scale_size(self, scale = None):
        if not scale:#if None
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            return min(scale_w, scale_h)
        return scale

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    g = Game()
    g.run()
