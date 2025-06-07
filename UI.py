import ui_backpack  # Inventory, map, etc.
import ui_hud  # HUD elements like health bar, timers, etc.

class UI_manager():#initialised in game_objects, keep common UIs always in memory
    def __init__(self, game_objects):
        self.screen = game_objects.game.display.make_layer(game_objects.game.window_size)        
        self.uis = {
            'hud':        ui_hud.HUD(game_objects),
            'inventory':  ui_backpack.InventoryUI(game_objects),
            'map':        ui_backpack.MapUI(game_objects),
            'radna':     ui_backpack.RadnaUI(game_objects),
            'journal':     ui_backpack.JournalUI(game_objects),
            #'pause':      ui_menu.PauseMenuUI(game_objects),
            #'options':    OptionsUI(game_objects, ui_assets),
            # …etc.
        }

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
    def hud(self):
        return self.uis['hud']        