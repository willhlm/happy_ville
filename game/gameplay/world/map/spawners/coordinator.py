from .area_stamp_spawner import AreaStampSpawner
from .interactable_spawner import InteractableSpawner
from .platform_spawner import PlatformSpawner
from .static_spawner import StaticSpawner


class ObjectSpawner:
    def __init__(self, game_objects):
        self.platforms = PlatformSpawner(game_objects)
        self.statics = StaticSpawner(game_objects)
        self.area_stamps = AreaStampSpawner(game_objects)
        self.interactables = InteractableSpawner(game_objects)

    def load_paths(self, *args, **kwargs):
        return self.platforms.load_paths(*args, **kwargs)

    def load_platforms(self, *args, **kwargs):
        return self.platforms.load_platforms(*args, **kwargs)

    def load_statics(self, *args, **kwargs):
        return self.statics.load_statics(*args, **kwargs)

    def load_area_stamps(self, *args, **kwargs):
        return self.area_stamps.load_area_stamps(*args, **kwargs)

    def load_interactables(self, *args, **kwargs):
        return self.interactables.load_interactables(*args, **kwargs)
