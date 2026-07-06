from .hud import ui_hud  # HUD elements like health bar, timers, etc.
from .background_menu import BackgroundMenu
from .overlay_manager import OverlayManager
from .backpack_manager import BackpackUiManager

class UiManager():#initialised in game_objects, keep common UIs always in memory
    def __init__(self, game_objects):
        self.hud = ui_hud.HUD(game_objects)
        self.menu = BackgroundMenu(game_objects)
        self.overlay = OverlayManager(game_objects)
        self.backpack = BackpackUiManager(game_objects)
