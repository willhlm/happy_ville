from .base.base_ui import BaseUI
from gameplay.ui.components import MenuArrow

class Bank(BaseUI):#caled from mr banks
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.pointer = MenuArrow([0,0], self.game.game_objects)        
        self.pointer_index = [0,0]#position of box        
        self.surf = Bank.surf
        self.bg = Bank.bg

    def pool(game_objects):
        Bank.bg_size = [120,64]
        Bank.surf = ['withdraw','deposit','cancel']

    def render(self):
        super().render()
        self.blit_text()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def blit_text(self):
        self.game.game_objects.font.render_text_bg(
            self.game.screen_manager.screen,
            self.bg_size,
            position=(190, 150),
        )
        for index, text in enumerate(self.surf):
            self.game.game_objects.font.render(
                self.game.screen_manager.screen,
                text,
                position=(300, 160 + index * 10),
            )

    def blit_pointer(self):
        self.game.game_objects.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =(300,130+10*self.pointer_index[1]))#shader render              

    def handle_events(self,input):
        input.processed()             
        if input.pressed:#press
            if input.name == 'y':
                self.game.state_manager.exit_state()
            elif input.name in ('a', 'return'):
                self.select()
        if input.pressed and input.name == 'down':#down
            self.pointer_index[1] += 1
            self.pointer_index[1] = min(self.pointer_index[1],len(self.surf)-1)
        elif input.pressed and input.name == 'up':#up
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
