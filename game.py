import pygame
import states
import game_objects
import sys
import constants as C
import shaders

class Game():
    def __init__(self):
        #initiate all screens
        self.WINDOW_SIZE = C.window_size.copy()
        self.scale_size()#get the scale according to your display size
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        flags = pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF #| pygame.FULLSCREEN#pygame.SCALED | pygame.FULLSCREEN

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)#has to be before set_mode
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)

        self.screen = pygame.Surface(self.WINDOW_SIZE)#do not add .convert_alpha(), should be initiad before display, for some reason
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled, flags, vsync = 1)
        #need to be after display
        self.screen_shader = shaders.Shader(self.WINDOW_SIZE_scaled, self.WINDOW_SIZE_scaled, (0, 0), "shaders/vertex.txt", "shaders/default_frag.txt", self.screen)

        #initiate game related values
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
        #i = 0
        while True:
            shaders.clear((0, 0, 0))

            #tick clock
            self.clock.tick(self.fps)
            self.dt = 60/max(self.clock.get_fps(),30)#assert at least 30 fps (to avoid 0)
            #dt =1
            #print(self.clock.get_fps())
            #print(self.clock.tick(self.fps))
            #i+=1
            #if self.clock.get_fps() < 50:
            #    print(i)
        #        print(self.clock.get_fps())
        #        print(self.fps)
        #        i = 0

            #handle event
            self.event_loop()

            #update
            self.state_stack[-1].update()

            #render
            self.state_stack[-1].render()#render as usual with blit onto self.screeen
            self.screen_shader.render(self.screen)#this rener method takes care of rendering to the display

            #update display
            pygame.display.flip()

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
