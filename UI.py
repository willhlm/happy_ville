import ui_backpack  # Inventory, map, etc.
import ui_hud  # HUD elements like health bar, timers, etc.

class UI_manager():#initialised in game_objects, keep certain UIs in memory
    def __init__(self, game_objects):
        self.uis = {'hud': ui_hud.HUD(game_objects), 'backpack': ui_backpack.BackpackUI(game_objects)}#Ui's we want always in memory

    def update(self):
        self.active_ui.update()

    def render(self):                
        self.active_ui.render()

    def handle_events(self, input):                
        self.active_ui.handle_events(input)

    def set_ui(self, ui, **kwarg):     
        self.uis[ui].on_enter(**kwarg)   
        self.active_ui = self.uis[ui] 

    @property
    def backpack(self):
        return self.uis['backpack']

    @property
    def hud(self):
        return self.uis['hud']        