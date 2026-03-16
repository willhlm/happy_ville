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
        input.processed()           
        if input.pressed:#press
            if input.name =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif input.name =='up':
                self.ammount += 1
                self.ammount = min(self.ammount,self.game_objects.player.backpack.inventory.get_quantity('amber_droplet'))
            elif input.name =='right':
                self.ammount += 100
                self.ammount = min(self.ammount,self.game_objects.player.backpack.inventory.get_quantity('amber_droplet'))
            elif input.name == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)
            elif input.name=='a' or input.name=='return':
                self.select()

