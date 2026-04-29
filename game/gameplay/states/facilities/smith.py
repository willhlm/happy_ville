from .base.base_ui import BaseUI
from gameplay.ui.components import MenuArrow

class Smith(BaseUI):#called from mr smith
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.pointer = MenuArrow([0, 0], self.game.game_objects)
        self.init()#depends on frame
        self.pointer_index = [0,0]#position of box
        self.set_response('')

    def init(self):
        self.actions = ['upgrade','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def init_canvas(self,size=[64,64]):
        self.surf = list(self.actions)
        self.bg_size = size

    def set_response(self,text):
        self.respond = text

    def render(self):
        super().render()
        self.game.game_objects.shaders['colour']['colour'] = [255,255,255,255]
        self.blit_text()
        self.blit_pointer()
        self.blit_response()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def blit_text(self):
        self.game.game_objects.font.render_text_bg(
            self.game.screen_manager.screen,
            self.bg_size,
            position=(280, 120),
        )
        for index, text in enumerate(self.surf):
            self.game.game_objects.font.render(
                self.game.screen_manager.screen,
                text,
                position=(310, 135 + index * 10),
            )

    def blit_pointer(self):
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =(300,135+10*self.pointer_index[1]),shader = self.game.game_objects.shaders['colour'])#shader render                        

    def blit_response(self): 
        self.game.game_objects.font.render(
            self.game.screen_manager.screen,
            self.respond,
            position=(300, 195),
        )

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

    def select(self):
        if self.pointer_index[1] == 0:#if we select upgrade
            self.upgrade()
        else:#select cancel
            self.game.state_manager.exit_state()

    def upgrade(self):
        if self.game.game_objects.player.inventory['Tungsten'] >= self.game.game_objects.player.sword.get_upgrade_cost():
            self.game.game_objects.player.sword.level_up()
            self.set_response('Now it is better')
        else:#not enough tungsten
            self.set_response('You do not have enough heavy rocks')
