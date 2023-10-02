import pygame
import states
import game_objects
import sys
import constants as C
import shaders
import pygame_light2d

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale_size()#get the scale according to your display size
        window_size_scaled = tuple([int(x*self.scale) for x in self.window_size])
        flags = pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF #| pygame.FULLSCREEN#pygame.SCALED | pygame.FULLSCREEN

        self.screen = pygame.Surface(self.window_size)#do not add .convert_alpha(), should be initiad before display, for some reason
        self.display = pygame.display.set_mode(window_size_scaled, flags, vsync = 1)
        self.lights_engine = pygame_light2d.LightingEngine(screen_res = window_size_scaled, native_res=self.window_size, lightmap_res=(int(self.window_size[0]/2.5), int(self.window_size[1]/2.5)))#need to be after display

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
        rect = pygame.Rect(0, 0, self.window_size[0], self.window_size[1])
        while True:
            self.lights_engine.clear(255, 255, 255, 255)

            #tick clock
            self.clock.tick(C.fps)
            self.dt = 60/max(self.clock.get_fps(),30)#assert at least 30 fps (to avoid 0)

            #handle event
            self.event_loop()

            #update
            self.state_stack[-1].update()

            #render
            self.state_stack[-1].render()#render as usual with blit onto self.screeen
            #shader render
            tex = self.lights_engine.surface_to_texture(self.screen)
            self.lights_engine.render_texture(tex, pygame_light2d.BACKGROUND, rect, rect)
            self.lights_engine.render()
            tex.release()#prevent memory leak

            #update display
            pygame.display.flip()

    def scale_size(self, scale = None):
        if scale:
            self.scale = scale
        else:
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            self.scale = min(scale_w,scale_h)

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)#has to be before set_mode
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)#has to be before set_mode
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)#has to be before set_mode
    g = Game()
    g.run()
