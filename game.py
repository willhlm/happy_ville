import pygame
import states
import game_objects
import Read_files

class Game():
    def __init__(self):

        #set all screens
        self.WINDOW_SIZE = (480,270)
        self.scale = 3
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen = pygame.Surface(self.WINDOW_SIZE)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled,vsync = 1)

        #misc
        self.game_objects = game_objects.Game_Objects(self)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.state_stack = [states.Title_Menu(self)]#,'Menu':States.Menu:,'Gameplay':States.Gameplay}
        self.controller = Read_files.Controller()

    def event_loop(self):
        for event in pygame.event.get():
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
            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen

            #update display
            pygame.display.update()

if __name__ == '__main__':
    pygame.init()#initilise
    g=Game()
    g.run()
