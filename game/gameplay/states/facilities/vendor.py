from .base.base_ui import BaseUI
from gameplay.ui.elements import MenuBox
from gameplay.ui.ui_loader import UI_loader
from gameplay.entities.items import AmberDroplet

class Vendor(BaseUI):#called from Astrid
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.vendor_UI = UI_loader.Vendor(self.game.game_objects)
        self.bg_pos = (70,20)

        self.init()
        self.letter_frame = 0
        self.pointer_index = [0,0]
        self.pointer = MenuBox(self.game.game_objects)
        self.item_index = [0,0]#pointer of item

    def init(self):
        self.init_canvas()

    def init_canvas(self):     
        self.items = []
        for item in self.npc.inventory.keys():
            item = getattr(sys.modules[entities_ui.__name__], item)([0,0],self.game.game_objects)#make the object based on the string
            self.items.append(item)

        self.amber = AmberDroplet([0,0],self.game.game_objects)#the thing showing how much money you have

        self.display_number = min(len(self.vendor_UI.objects), len(self.items))#number of items to list
        self.sale_items = self.items[0:self.display_number]#gets udated when you press the up down keys

        self.buy_sur = self.game.game_objects.font.render(text = 'Buy')
        self.cancel_sur = self.game.game_objects.font.render(text = 'Cancel')

    def set_response(self,text):
        self.respond = self.game.game_objects.font.render(text = text)

    def blit_response(self):
        self.game.display.render(self.respond, self.game.screen_manager.screen, position = (190,150))#shader render

    def update(self):
        self.letter_frame += self.game.game_objects.game.dt

    def render(self):
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.blit_BG()
        self.blit_money()
        self.blit_description()
        self.blit_items()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def blit_BG(self):
        self.game.display.render(self.vendor_UI.BG, self.game.screen_manager.screen, position = self.bg_pos)#shader render

    def blit_money(self):#blit how much gold we have in inventory
        money = self.game.game_objects.player.backpack.inventory.get_quantity('amber_droplet')
        count_text = self.game.game_objects.font.render(text = str(money))
        position = [self.bg_pos[0] + self.vendor_UI.amber.rect.bottomright[0], self.bg_pos[1] + self.vendor_UI.amber.rect.bottomright[1]]
        self.game.display.render(count_text, self.game.screen_manager.screen, position = position, shader = self.game.game_objects.shaders['colour'])#shader render

        self.amber.animation.update()
        position = [self.bg_pos[0] + self.vendor_UI.amber.rect.topleft[0], self.bg_pos[1] + self.vendor_UI.amber.rect.topleft[1]]
        self.game.display.render(self.amber.image, self.game.screen_manager.screen, position = position)#shader render

    def blit_description(self):
        conv=self.items[self.item_index[1]].description        
        text = self.game.game_objects.font.render(self.vendor_UI.description['size'], conv, int(self.letter_frame//2))
        position = [self.bg_pos[0] + self.vendor_UI.description['position'][0], self.bg_pos[1] + self.vendor_UI.description['position'][1]]
        self.game.display.render(text, self.game.screen_manager.screen, position = position, shader = self.game.game_objects.shaders['colour'])#shader render

    def blit_items(self):
        for index, item in enumerate(self.sale_items):            
            item.animation.update()
            position = [self.bg_pos[0] + self.vendor_UI.objects[index].rect.topleft[0], self.bg_pos[1] + self.vendor_UI.objects[index].rect.topleft[1]]
            self.game.display.render(item.image, self.game.screen_manager.screen, position = position)#shader render

            #blit cost
            item_name=str(type(item).__name__)
            cost = self.npc.inventory[item_name]
            cost_text = self.game.game_objects.font.render(text = str(cost))
            position = [self.bg_pos[0] + self.vendor_UI.objects[index].rect.bottomright[0], self.bg_pos[1] + self.vendor_UI.objects[index].rect.bottomright[1]]
            self.game.display.render(cost_text, self.game.screen_manager.screen, position = position, shader = self.game.game_objects.shaders['colour'])#shader render                
            
    def blit_pointer(self):
        position = [self.bg_pos[0] + self.vendor_UI.objects[self.pointer_index[1]].rect.topleft[0], self.bg_pos[1] + self.vendor_UI.objects[self.pointer_index[1]].rect.topleft[1]]
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, position = position)#shader render

    def handle_events(self, input):
        event = input.output()
        input.processed()            
        if event[0]:#press
            if event[-1] == 'y':
                self.game.state_manager.exit_state()

            elif event[-1] =='down':
                self.item_index[1] += 1
                self.item_index[1] = min(self.item_index[1],len(self.items)-1)

                if self.pointer_index[1] == self.display_number-1:#at the bottom of the list
                    self.sale_items = self.items[self.item_index[1]-self.display_number+1:self.item_index[1]+1]
                
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],self.display_number-1)                                    
                self.letter_frame = 0                    

            elif event[-1] =='up':
                self.item_index[1]-=1
                self.item_index[1] = max(self.item_index[1],0)

                if self.pointer_index[1]==0:
                    self.sale_items = self.items[self.item_index[1]:self.item_index[1]+self.display_number]

                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
                self.letter_frame = 0

            elif event[-1]=='a' or event[-1]=='return':
                self.select()

    def select(self):
        item = type(self.items[self.item_index[1]]).__name__
        self.game_state.state.append(Vendor2(self.game_state,self.npc,item))#go to next frame

