from .base.base_ui import BaseUI
from gameplay.ui.loaders import FastTravelLoader
from gameplay.ui.components import MenuBox

class FastTravelMenu(BaseUI):
    def __init__(self, game):
        super().__init__(game)
        self.travel_UI = FastTravelLoader(self.game.game_objects)
        self.index = [0,0]
        self.define_destination()
        self.pointer = MenuBox(self.game.game_objects)

    def define_destination(self):
        self.destinations = []
        for level in self.game.game_objects.world_state.travel_points.keys():
            self.destinations.append(level)

    def blit_BG(self):        
        self.game.display.render(self.travel_UI.BG, self.game.screen_manager.screen)#shader render                

    def blit_destinations(self):
        for index, name in enumerate(self.game.game_objects.world_state.travel_points.keys()):
            text = self.game.game_objects.font.render((152,80), name, 100)
            self.game.display.render(text, self.game.screen_manager.screen, position =self.travel_UI.name_pos[index])#shader render                

    def blit_pointer(self):
        pos = self.travel_UI.name_pos[self.index[0]]
        self.game.display.render(self.pointer.image, self.game.screen_manager.screen, position =pos)#shader render                

    def render(self):
        self.blit_BG()
        self.blit_destinations()
        self.blit_pointer()
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def handle_events(self,input):
        event = input.output()
        input.processed()              
        if event[0]:#press
            if event[-1] == 'select':
                self.game.state_manager.exit_state()

            elif event[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.destinations)-1)

            elif event[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif event[-1] == 'a':
                self.game.state_manager.exit_state()
                level = self.destinations[self.index[0]]
                cord = self.game_objects.world_state.travel_points[level]
                self.game_objects.load_map(self,level,cord)

