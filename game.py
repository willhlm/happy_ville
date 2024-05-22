import pygame, sys
import states
import game_objects
import constants as C
from pygame_render import RenderEngine

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale = self.scale_size()#get the scale according to your display size
        window_size_scaled = [int(self.window_size[0] * self.scale), int(self.window_size[1] * self.scale)]

        self.display = RenderEngine(window_size_scaled[0],window_size_scaled[1])
        self.screen = self.display.make_layer(self.window_size)

        #initiate game related values
        self.clock = pygame.time.Clock()
        self.game_objects = game_objects.Game_Objects(self)
        self.state_stack = [states.Title_Menu(self)]

        #debug flags
        self.DEBUG_MODE = True
        self.RENDER_FPS_FLAG = True
        self.RENDER_HITBOX_FLAG = True
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN])
        pygame.event.set_blocked([pygame.TEXTINPUT])#for some reason, there is a text input here and there. So, blocking it

    def event_loop(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.game_objects.controller.map_inputs(event)
                self.state_stack[-1].handle_events(self.game_objects.controller.output())

    def run(self):
        while True:
            self.screen.clear(0, 0, 0, 0)

            #tick clock
            self.clock.tick(120)
            self.dt = 60/max(self.clock.get_fps(),30)#assert at least 30 fps (to avoid 0)
            #handle event
            self.event_loop()

            #update
            self.state_stack[-1].update()

            #render
            self.state_stack[-1].render()#render onto self.screeen
            self.display.render(self.screen.texture, self.display.screen, scale = self.scale)#shader render

            #update display
            pygame.display.flip()

    def scale_size(self, scale = None):
        if not scale:#if None
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            scale = min(scale_w, scale_h)
        return scale

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    g = Game()
    g.run()
