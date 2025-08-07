import pygame, sys, time, statistics
import game_objects
import constants as C
import read_files
import state_manager
from pygame_render import RenderEngine
import screen_manager
#pygame.print_debug_info()

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale = self.scale_size(2)#get the scale according to your display size
        display_size = [int(self.window_size[0] * self.scale), int(self.window_size[1] * self.scale)]
        game_settings = read_files.read_json('game_settings.json')['display']

        self.display = RenderEngine(display_size[0] - self.scale, display_size[1] - self.scale, fullscreen = game_settings['fullscreen'], vsync = game_settings['vsync'])        
        self.screen_manager = screen_manager.ScreenManager(self)
        self.screen = self.display.make_layer(self.window_size)#the "main" screen ''rendered last''

        #initiate game related values
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.game_objects = game_objects.Game_Objects(self)
        self.state_manager = state_manager.State_manager(self, 'Title_menu')

        #debug flags
        self.DEBUG_MODE = True
        self.RENDER_FPS_FLAG = True
        self.RENDER_HITBOX_FLAG = True
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN])
        pygame.event.set_blocked([pygame.TEXTINPUT])#for some reason, there is a text input here and there. So, blocking it

    def event_loop(self):
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
        self.game_objects.input_interpreter.update()#checks for flicks and other input related things
        for input in inputs:
            input.update(self.dt)
            self.state_manager.handle_events(input)

    def run(self):
        frame_stats = FrameStats()
        prev_time = time.perf_counter()
        while True:
            self.screen.clear(0, 0, 0, 0)
            for screen in list(self.screen_manager.screens.values()):
                screen.layer.clear(0, 0, 0, 0)

            frame_end = time.perf_counter()
            self.dt =60* min(frame_end - prev_time, 2/C.fps)
            prev_time = frame_end
            frame_stats.record_frame(self.dt/60)

            #tick clock            
            #self.dt = 60/max(self.clock.get_fps(),30)#assert at least 30 fps (to avoid 0)
            #frame_stats.record_frame(self.dt / 60)
            #handle event
            self.event_loop()

            #update
            self.state_manager.update()

            #render
            self.state_manager.render()
            
            #display rendering
            self.screen_manager.render()#render multiple screen, and make it pixel perfect to the display
            self.display.render(self.screen.texture, self.display.screen, scale = self.scale)#render the main screen

            #update display
            pygame.display.flip()
            self.clock.tick(C.fps)

    def scale_size(self, scale = None):
        if not scale:#if None
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            return min(scale_w, scale_h)
        return scale


class FrameStats:
    def __init__(self, log_interval=3.0, max_samples=300):
        self.frame_times = []
        self.log_interval = log_interval
        self.max_samples = max_samples
        self._log_timer = 0.0
        self._last_log_time = time.perf_counter()

    def record_frame(self, frame_time_sec):
        ms = frame_time_sec * 1000  # convert to milliseconds
        self.frame_times.append(ms)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)

        now = time.perf_counter()
        self._log_timer += now - self._last_log_time
        self._last_log_time = now

        if self._log_timer >= self.log_interval:
            self._log_timer = 0.0
            self.log_stats()

    def log_stats(self):
        if not self.frame_times:
            return
        avg = statistics.mean(self.frame_times)
        stddev = statistics.stdev(self.frame_times) if len(self.frame_times) > 1 else 0.0
        worst = max(self.frame_times)
        best = min(self.frame_times)
        print(f"[Frame Stats] Avg: {avg:.2f} ms | Jitter: ±{stddev:.2f} ms | Best: {best:.2f} ms | Worst: {worst:.2f} ms")


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    g = Game()
    g.run()
