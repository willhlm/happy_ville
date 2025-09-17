import pygame, sys, time
from engine import constants as C
from engine.utils import read_files
from engine.system import state_manager
from engine.render.screen_manager import ScreenManager
from pygame_render import RenderEngine
from engine import game_objects

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale = self.scale_size(2)#get the scale according to your display size
        self.display_size = [int(self.window_size[0] * self.scale), int(self.window_size[1] * self.scale)]
        game_settings = read_files.read_json('saves/game_settings.json')['display']
        self.display = RenderEngine(self.display_size[0] - self.scale, self.display_size[1] - self.scale, fullscreen = game_settings['fullscreen'], vsync = game_settings['vsync']) #vsync -1 may be good for mac
        self.screen_manager = ScreenManager(self)

        #initiate game related values
        self.game_loop = GameLoop(self)
        self.game_objects = game_objects.Game_Objects(self)
        self.state_manager = state_manager.State_manager(self, 'title_menu')

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
        self.game_loop.run()

    def scale_size(self, scale = None):
        if not scale:#if None
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            return min(scale_w, scale_h)
        return scale

    def render_display(self, texture, scale = True):#called from game states
        if scale: scale = self.scale
        else: scale = 1
        self.display.render(texture, self.display.screen, scale = scale)

class GameLoop():
    def __init__(self, game):
        self.game = game
        self.clock = pygame.time.Clock()
        self.fixed_dt = 1.0 / 60.0# 60Hz physics step in seconds
        self.accumulator = 0.0
        self.alpha = 0.0

    def run(self):
        prev_time = time.perf_counter()
        while True:
            self.game.screen_manager.clear()

            # Calculate frame time in seconds
            frame_end = time.perf_counter()
            raw_frame_time = min(frame_end - prev_time, 2.0 / C.fps)  # Cap large jumps
            prev_time = frame_end
            dt = max(raw_frame_time, 0.001)# Avoid zero or negative dt

            # Add to accumulator (in seconds)
            self.accumulator += dt

            # Event handling (in frames)
            self.game.event_loop(dt * 60)

            # Fixed timestep updates (in frames)
            while self.accumulator >= self.fixed_dt:
                self.game.state_manager.update(self.fixed_dt * 60)
                self.accumulator -= self.fixed_dt

            # Interpolation factor for rendering
            self.alpha = self.accumulator / self.fixed_dt
            self.game.state_manager.update_render(dt * 60)
            self.game.state_manager.render()

            # Update display and limit FPS
            pygame.display.flip()
            self.clock.tick(C.fps)

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    g = Game()
    g.run()
