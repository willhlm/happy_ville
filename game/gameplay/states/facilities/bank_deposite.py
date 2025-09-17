from .bank import Bank

class BankDeposite(Bank):#caled from mr banks
    def __init__(self, game, npc):
        super().__init__(game, npc)
        self.ammount = 0

    def select(self):
        self.game.game_objects.player.backpack.inventory.remove('amber_droplet', self.ammount)
        self.npc.ammount+=self.ammount
        self.game_state.state.pop()

    def blit_text(self):
        self.game_objects.game.display.render(self.bg, self.game.screen_manager.screen, position = (280,120))#shader render         
        self.amount_surf = self.game_objects.font.render(text = str(self.ammount))
        self.game_objects.game.display.render(self.amount_surf, self.game.screen_manager.screen, position = (310,130))#shader render         

    def blit_pointer(self):
        pass

    def handle_events(self,input):
        event = input.output()
        input.processed()           
        if event[0]:#press
            if event[-1] =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif event[-1] =='up':
                self.ammount += 1
                self.ammount = min(self.ammount,self.game_objects.player.backpack.inventory.get_quantity('amber_droplet'))
            elif event[-1] =='right':
                self.ammount += 100
                self.ammount = min(self.ammount,self.game_objects.player.backpack.inventory.get_quantity('amber_droplet'))
            elif event[-1] == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)
            elif event[-1]=='a' or event[-1]=='return':
                self.select()

