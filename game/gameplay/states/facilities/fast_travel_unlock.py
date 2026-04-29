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
        self.define_pos()
        self.pointer = MenuBox(self.game.game_objects)

    def define_pos(self):
        self.pos = []
        for i in range(0,len(self.actions)):
            self.pos.append([255+i*30,110])

    def blit_BG(self):
        pos = [self.game.window_size[0]*0.5-self.bg_size[0]*0.5,self.game.window_size[1]*0.25]
        self.game.game_objects.font.render_text_bg(
            self.game.screen_manager.screen,
            self.bg_size,
            position=pos,
        )

    def blit_actions(self):
        for index, action in enumerate(self.actions):
            self.game.game_objects.font.render(
                self.game.screen_manager.screen,
                action,
                position=self.pos[index],
            )

    def blit_text(self):
        self.game.game_objects.font.render(
            self.game.screen_manager.screen,
            self.conv,
            position=(220, 90),
            width=130,
            letter_frame=int(self.letter_frame // 2),
        )

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
        input.processed()           
        if input.pressed:#press
            if input.name == 'select':
                self.game.state_manager.exit_state()

            elif input.name == 'right':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.pos)-1)

            elif input.name == 'left':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif input.name in ('a', 'return'):
                if self.index[0] == 1:#no
                    self.game.state_manager.exit_state()
                elif self.index[0] == 0:#yes
                    if self.fast_travel.unlock():#enough money: unlocked
                        self.game.state_manager.exit_state()
                    else:#not enout money
                        pass
