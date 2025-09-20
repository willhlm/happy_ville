from .base.base_ui import BaseUI
from gameplay.ui.components import MenuBox

class FastTravelUnlock(BaseUI):
    def __init__(self, game, fast_travel):
        super().__init__(game)
        self.fast_travel = fast_travel
        self.index = [0,0]
        self.letter_frame = 0
        self.actions = ['yes','no']
        self.conv = 'Would you like to offer ' + str(self.fast_travel.cost) + ' ambers to this statue?'
        self.bg_size = [152,48]
        self.bg = self.game.game_objects.font.fill_text_bg(self.bg_size)
        self.define_pos()
        self.pointer = MenuBox(self.game.game_objects)

    def define_pos(self):
        self.pos = []
        for i in range(0,len(self.actions)):
            self.pos.append([255+i*30,110])

    def blit_BG(self):
        pos = [self.game.window_size[0]*0.5-self.bg_size[0]*0.5,self.game.window_size[1]*0.25]
        self.game.display.render(self.bg, self.game.screen_manager.screen, position = pos)#shader render

    def blit_actions(self):
        for index, action in enumerate(self.actions):
            response = self.game.game_objects.font.render(text = action)
            self.game.display.render(response, self.game.screen_manager.screen, position = self.pos[index])#shader render

    def blit_text(self):
        text = self.game.game_objects.font.render((130,90), self.conv, int(self.letter_frame//2))
        self.game.display.render(text, sself.game.screen_manager.screen, position =(220,90))#shader render        

    def blit_pointer(self):
        pos = self.pos[self.index[0]]
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =pos)#shader render        
        
    def update(self):
        self.letter_frame += self.game.dt

    def render(self):
        self.blit_BG()
        self.blit_actions()
        self.blit_text()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def handle_events(self,input):
        event = input.output()
        input.processed()           
        if event[0]:#press
            if event[-1] == 'select':
                self.game.state_manager.exit_state()

            elif event[-1] =='right':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.pos)-1)

            elif event[-1] =='left':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif event[-1] == 'a' or 'return':
                if self.index[0] == 1:#no
                    self.game.state_manager.exit_state()
                elif self.index[0] == 0:#yes
                    if self.fast_travel.unlock():#enough money: unlocked
                        self.game.state_manager.exit_state()
                    else:#not enout money
                        pass

