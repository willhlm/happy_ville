from .vendor import Vendor

class Vendor_2(Vendor):#called from vendor when selecting an item
    def __init__(self, game, npc, item):
        super().__init__(game, npc)
        self.item = item

    def init(self):
        self.bg2 = self.game.game_objects.font.fill_text_bg([64,32])
        self.init_canvas()

    def render(self):
        self.blit_BG2()
        self.blit_pointer()        
        super().render()

    def blit_BG2(self):
        self.game.display.render(self.buy_sur, self.game.screen_manager.screen,(280+30,120+10))#shader render        
        self.game.display.render(self.cancel_sur, self.game.screen_manager.screen,(280+30,120 + 20))#shader render        
        self.game.display.render(self.bg2, self.game.screen_manager.screen,(280,120))#shader render

    def blit_pointer(self):
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, (300, 130 + 10 * self.pointer_index[1]))#shader render

    def select(self):
        if self.pointer_index[1] == 0:#if we select buy
            self.buy()
        else:
            self.set_response('What do you want?')
        self.game.state_manager.enter_state('Vendor', category = 'game_states_facilities')

    def buy(self):
        if self.game.game_objects.player.inventory['Amber_Droplet']>=self.npc.inventory[self.item]:
            self.game.game_objects.player.inventory[self.item] += 1
            self.game.game_objects.player.inventory['Amber_Droplet']-=self.npc.inventory[self.item]
            self.set_response('Thanks for buying')
        else:#not enough money
            self.set_response('Get loss you poor piece of shit')

    def handle_frame2(self,input):
        event = input.output()
        input.processed()             
        if event[0]:#press
            if event[-1] == 'y':
                self.game.state_manager.exit_state()
            elif event[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],1)
            elif event[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif event[-1]=='a' or event[-1]=='return':
                self.select()
