from . import ui_backpack  # Inventory, map, etc.
from . import ui_hud  # HUD elements like health bar, timers, etc.

class UI_manager():#initialised in game_objects, keep common UIs always in memory
    def __init__(self, game_objects):
        self.screen = game_objects.game.display.make_layer(game_objects.game.window_size)        
        self.uis = {
            'hud':        ui_hud.HUD(game_objects),
            'inventory':  ui_backpack.InventoryUI(game_objects),
            'map':        ui_backpack.MapUI(game_objects),
            'worldmap':        ui_backpack.MapUI_2(game_objects),
            'radna':     ui_backpack.RadnaUI(game_objects),
            'journal':     ui_backpack.JournalUI(game_objects),            
        }
        self.index = 1#start at inventory
        self.backpack = list(game_objects.player.backpack.holdings.keys())#the things player has access to

    def update(self, dt):
        self.active_ui.update(dt)

    def render(self):                
        self.active_ui.render()

    def handle_events(self, input):                
        self.active_ui.handle_events(input)

    def set_ui(self, ui, **kwarg):     
        self.uis[ui].on_enter(**kwarg)   
        self.active_ui = self.uis[ui] 
    
    def next_page(self, **kwarg):
        self.index += 1        
        self.index = min(self.index, len(self.backpack))
        self.set_ui(self.backpack[self.index], **kwarg)

    def previouse_page(self, **kwarg):
        self.index -= 1        
        self.index = max(self.index, 0)
        self.set_ui(self.backpack[self.index], **kwarg)        

    @property
    def hud(self):
        return self.uis['hud']        