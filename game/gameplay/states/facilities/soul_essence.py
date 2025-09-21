from .base.base_ui import BaseUI
from gameplay.ui.components import MenuBox

class SoulEssence(BaseUI):#called from inorinoki
    def __init__(self, game):
        super().__init__(game)
        self.actions=['health','spirit','cancel']
        self.pointer = MenuBox(self.game.game_objects)
        self.cost = 4
        self.pointer_index = [0,0]
        self.init_canvas()
        self.bg_pos = [280,120]

    def init_canvas(self,size=[64,64]):
        self.surf=[]
        self.bg = self.game.game_objects.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.game.game_objects.font.render(text = string))

    def render(self):
        super().render()
        self.blit_BG()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def blit_pointer(self):
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =  (self.bg_pos[0] + 30,self.bg_pos[1] + 10+self.pointer_index[1]*10))#shader render 

    def blit_BG(self):
        self.game.display.render(self.bg, self.game.screen_manager.screen, position = self.bg_pos)#shader render        
        for index, surf in enumerate(self.surf):
            self.game.display.render(surf, self.game.screen_manager.screen, position = (self.bg_pos[0] + 30,self.bg_pos[1] + 10+index*10))#shader render        

    def handle_events(self,input):
        event = input.output()
        input.processed()           
        if event[0]:#press
            if event[-1] == 'y':
                self.game.state_manager.exit_state()
            elif event[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],len(self.actions)-1)
            elif event[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif event[-1]=='a' or event[-1]=='return':
                self.select()

    def select(self):
        if self.pointer_index[1] == 0:#if we select health
            if self.game.game_objects.player.backpack.inventory.get_quantity('soul_essence') >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                heart = HeartContainer(pos,self.game.game_objects)
                self.game.game_objects.loot.add(heart)
                self.game.game_objects.player.backpack.inventory.remove('soul_essence', self.cost)
        elif self.pointer_index[1] == 1:#if we select spirit
            if self.game.game_objects.player.backpack.inventory.get_quantity('soul_essence') >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                spirit = SpiritContainer(pos,self.game.game_objects)
                self.game.game_objects.loot.add(spirit)
                self.game.game_objects.player.backpack.inventory.remove('soul_essence', self.cost)
        else:#select cancel
            self.game.state_manager.exit_state()

