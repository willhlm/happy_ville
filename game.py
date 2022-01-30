import pygame
import states
import game_objects
import Read_files
import sys

class Game():
    def __init__(self):

        #initiate should implement a init file to read values for thing sin game, like screen scale, fps etc.

        #initiate all screens
        self.WINDOW_SIZE = (480,270)
        self.scale_size()#get the scale according to your display size
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen = pygame.Surface(self.WINDOW_SIZE)
        flags = pygame.SCALED# | pygame.FULLSCREEN
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled,flags,vsync = 1)


        #initiate game related values
        self.game_objects = game_objects.Game_Objects(self)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.state_stack = [states.Title_Menu(self)]#,'Menu':states.Menu:,'Gameplay':states.Gameplay}
        self.controller = Read_files.Controller()

    def event_loop(self):

        for event in pygame.event.get():
            #print(event)

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            else:
                self.controller.map_inputs(event)
                self.state_stack[-1].handle_events(self.controller.output())

    def run(self):
        while True:
            #tick clock
            self.clock.tick(self.fps)#=dt

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
        scale_w=pygame.display.Info().current_w/self.WINDOW_SIZE[0]
        scale_h=pygame.display.Info().current_h/self.WINDOW_SIZE[1]
        if scale:
            self.scale = scale
        else:
            self.scale = min(scale_w,scale_h)


if __name__ == '__main__':
    pygame.init()#initilise
    g=Game()
    g.run()
