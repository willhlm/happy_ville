from .base.base_ui import BaseUI
from gameplay.ui.elements import MenuArrow

class Bank(BaseUI):#caled from mr banks
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.pointer = MenuArrow([0,0], self.game.game_objects)        
        self.pointer_index = [0,0]#position of box        
        self.surf = Bank.surf
        self.bg = Bank.bg

    def pool(game_objects):
        size = [120,64]
        surf = []
        Bank.bg = game_objects.font.fill_text_bg(size)
        actions = ['withdraw','deposit','cancel']
        for string in actions:
            surf.append(game_objects.font.render(text = string))
        Bank.surf = surf

    def render(self):
        super().render()
        self.blit_text()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def blit_text(self):
        self.game.game_objects.game.display.render(self.bg, self.game.screen_manager.screen, position = (190,150))#shader render        
        for index, surf in enumerate(self.surf):
            self.game.game_objects.game.display.render(surf, self.game.screen_manager.screen, position = (300,160+index*10))#shader render

    def blit_pointer(self):
        self.game.game_objects.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =(300,130+10*self.pointer_index[1]))#shader render              

    def handle_events(self,input):
        event = input.output()
        input.processed()             
        if event[0]:#press
            if event[-1] == 'y':
                self.game.state_manager.exit_state()
            elif event[-1]=='a' or event[-1]=='return':
                self.select()
        if event[2]['l_stick'][1] > 0 or (event[-1] == 'dpad_down' and event[0]):#down
            self.pointer_index[1] += 1
            self.pointer_index[1] = min(self.pointer_index[1],len(self.surf)-1)
        elif event[2]['l_stick'][1] < 0 or (event[-1] == 'dpad_up' and event[0]):#up
            self.pointer_index[1] -= 1
            self.pointer_index[1] = max(self.pointer_index[1],0)                

    def select(self):#exchane of money
        if self.pointer_index[1]==2:#cancel
            self.game.state_manager.exit_state()
        else:#widthdraw or deposit
            if self.pointer_index[1]==0:#widthdraw
                self.game.game_objects.UI.set_ui('Bank_withdraw', self.npc)
            else:#deposite
                self.game.game_objects.UI.set_ui('Bank_deposite', self.npc)            

