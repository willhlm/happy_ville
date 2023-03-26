import pygame
import states
import game_objects
import Read_files
import sys
import constants as C

class Game():
    def __init__(self):
        #initiate all screens
        self.WINDOW_SIZE = C.window_size.copy()
        self.scale_size()#get the scale according to your display size
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen = pygame.Surface(self.WINDOW_SIZE)#do not add .convert_alpha()
        flags = pygame.SCALED# | pygame.FULLSCREEN
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled,flags,vsync = 1)

        #initiate game related values and mixer
        #pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.game_objects = game_objects.Game_Objects(self)
        self.fps = C.fps
        self.state_stack = [states.Title_Menu(self)]

        #debug flags
        self.DEBUG_MODE = True
        self.RENDER_FPS_FLAG = True
        self.RENDER_HITBOX_FLAG = True
        #pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

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
            #tick clock
            self.clock.tick(self.fps)
            self.dt = 60/max(self.clock.get_fps(),30)#assert at least 30 fps (to avoid 0)
            #self.dt = 1
            #handle event
            self.event_loop()

            #update
            self.state_stack[-1].update()

            #render
            self.state_stack[-1].render()

            #update display
            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
            pygame.display.update()

    def scale_size(self, scale = None):
        if scale:
            self.scale = scale
        else:
            scale_w=pygame.display.Info().current_w/self.WINDOW_SIZE[0]
            scale_h=pygame.display.Info().current_h/self.WINDOW_SIZE[1]
            self.scale = min(scale_w,scale_h)

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise    
    g = Game()
    g.run()
