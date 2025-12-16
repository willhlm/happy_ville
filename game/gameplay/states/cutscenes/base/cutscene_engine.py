from gameplay.states.gameplay.gameplay import Gameplay
from gameplay.entities.visuals.cosmetics import SpawnEffect
from engine.utils import read_files
from engine.system import animation
from gameplay.entities.visuals.particles import particles

class CutsceneEngine(Gameplay):#cut scenens that is based on game engien
    def __init__(self,game):
        super().__init__(game)
        self.timer = 0
        self.pos = [-self.game.window_size[1],self.game.window_size[1]]
        self.const = [0.8,0.8]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.rect1 = game.display.make_layer(self.game.window_size)#TODO
        self.rect2 = game.display.make_layer(self.game.window_size)#TODO

        self.rect2.clear(0,0,0,255)
        self.rect1.clear(0,0,0,255)

    def update_render(self, dt):
        super().update_render(dt)
        self.pos[0] += dt#the upper balck box
        self.pos[1] -= dt#the lower balck box

        self.pos[0] = min(-self.game.window_size[1]*self.const[0], self.pos[0])
        self.pos[1] = max(self.game.window_size[1]*self.const[1], self.pos[1])        

    def render(self):
        super().render()
        self.cinematic()

    def handle_movement(self):
        pass

    def cinematic(self):#black box stuff
        self.game.display.render(self.rect1.texture, self.game.screen_manager.screen, position = [0,self.pos[0]])
        self.game.display.render(self.rect2.texture,  self.game.screen_manager.screen, position = [0,self.pos[1]])
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] == 'a':
                self.press = True
