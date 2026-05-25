import pygame
from engine.utils import read_files

from gameplay.entities.items.base.components import ItemInteractComponent
from .world_item import WorldItem


class InteractWorldItem(WorldItem):
    _pickup_ui_image_cache = {}
    pickup_fx = {
        'fade': {
            'state': 'Alpha',
            'alpha': 255,
            'fade_rate': 0.9,
            'kill_threshold': 10,
        },
        'sound': {
            'key': 'interact',
            'volume': 0.4,
        },
        'particles': {
            'preset': 'burst',
            'count': 18,
            'colour': [255, 255, 255, 255],
        },
    }

    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.interact_component = ItemInteractComponent(self, **kwargs)
        self.is_interacting = False

    @classmethod
    def get_pickup_title(cls):
        return cls.get_item_definition().title

    @classmethod
    def get_pickup_text(cls):
        pickup_text = cls.get_item_definition().pickup_text
        if pickup_text == '':
            raise ValueError(f"{cls.__name__}.item_definition.pickup_text must be set")
        return pickup_text

    @classmethod
    def get_pickup_ui_image_path(cls):
        pickup_ui_image_path = cls.get_item_definition().pickup_ui_image_path
        if pickup_ui_image_path == '':
            raise ValueError(
                f"{cls.__name__}.item_definition.pickup_ui_image_path must be set"
            )
        return pickup_ui_image_path

    def get_pickup_image(self):
        path = self.get_pickup_ui_image_path()
        return InteractWorldItem._pickup_ui_image_cache[path]

    @classmethod
    def get_pickup_fx(cls):
        pickup_fx = {}
        for section, config in InteractWorldItem.pickup_fx.items():
            pickup_fx[section] = config.copy() if isinstance(config, dict) else config

        for section, config in getattr(cls, 'pickup_fx', {}).items():
            if isinstance(config, dict) and section in pickup_fx and isinstance(pickup_fx[section], dict):
                pickup_fx[section].update(config)
            else:
                pickup_fx[section] = config

        return pickup_fx

    @classmethod
    def pool_interactable_sprite(cls, game_objects):
        cls.sprites['wild'] = read_files.load_sprites_list(
            'assets/sprites/entities/items/interactable_items/idle/',
            game_objects,
        ).textures

    @classmethod
    def pool_pickup_ui_images(cls, game_objects, paths=None):
        if paths is None:
            paths = [cls.get_pickup_ui_image_path()]

        for path in paths:
            if path in InteractWorldItem._pickup_ui_image_cache:
                continue
            surface = pygame.image.load(path).convert_alpha()
            InteractWorldItem._pickup_ui_image_cache[path] = (
                game_objects.game.display.surface_to_texture(surface)
            )

    def get_pickup_persistence_key(self):
        return self.get_item_id()

    def mark_picked_up(self):
        self.game_objects.world_state.objects.set_bool(
            self.game_objects.map.biome_room_name,
            'interactable_items',
            self.get_pickup_persistence_key(),
            True,
        )

    def interact(self, player):
        if self.consumed or self.is_interacting:
            return False
        self.is_interacting = True
        self.interact_component.interact_with_pickup_text(player)
        return True

    def on_pickup_interaction_complete(self, player):
        self.is_interacting = False
        return self.try_pickup(player)

    def kill(self):
        super().kill()
        self.interact_component.on_kill()
