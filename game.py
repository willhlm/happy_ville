import pygame
import States

class Game():
    def __init__(self):
        self.WINDOW_SIZE = (432,243)
        self.scale = 3
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.display=pygame.display.set_mode(self.WINDOW_SIZE_scaled,vsync = 1)
        self.clock=pygame.time.Clock()
        self.fps=60
        self.stack_states=[States.Splash(self)]#,'Menu':States.Menu:,'Gameplay':States.Gameplay}
        self.controller=Controller()

    def event_loop(self):
        for event in pygame.event.get():
            self.controller.translate_inputs(event)
            self.stack_states[-1].handle_events(self.controller.output)

    def run(self):
        while True:
            #tick clock
            self.clock.tick(self.fps)#=dt

            #handle event
            self.event_loop()

            #update
            self.stack_states[-1].update()

            #render
            self.stack_states[-1].render(self.display)

            #update display
            pygame.display.update()

pygame.init()#initilise
g=Game()
g.run()
