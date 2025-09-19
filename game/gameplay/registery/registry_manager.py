# gameplay/registry/bootstrap.py
from .items import REGISTER_ITEMS
from .npcs import REGISTER_NPCS
from .enemies import REGISTER_ENEMIES

class RegistryManager():
    def __init__(self):
        self.registry = {}
        self.load_registries()

    def load_registries(self):
        """Load all registries into a single organized dictionary."""
        self.registry = {
            "items": REGISTER_ITEMS,
            "npcs": REGISTER_NPCS,
            "enemies": REGISTER_ENEMIES,
            #"interactables": REGISTER_INTERACTABLES,
        }

    def fetch(self, category, key):
        """
        Get a class from a registry safely.
        
        Example:
            registry_manager.get("items", "potion")
        """
        return self.registry[category].get(key, None)

    def register(self, category, key, value):
        """
        Dynamically add a new class to a registry at runtime.
        """
        if not self.registry.get(category, False):
            self.registry[category] = {}
        self.registry[category][key] = value
