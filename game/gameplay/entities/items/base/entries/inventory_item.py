from dataclasses import dataclass, field

from engine.system.animation import Animation


@dataclass
class InventoryItem:
    item_id: str
    item_cls: type
    game_objects: object
    sprites: dict
    description: str
    inventory_animation_name: str
    image: object = field(init=False)
    animation: Animation = field(init=False)

    def __post_init__(self):
        animation_name = self.inventory_animation_name
        if animation_name not in self.sprites:
            animation_name = 'idle'
        self.inventory_animation_name = animation_name
        self.image = self.sprites[animation_name][0]
        self.animation = Animation(self, animation_name=animation_name)

    @classmethod
    def from_item_class(cls, item_cls, game_objects, item_id=None):
        definition = item_cls.get_item_definition()
        sprites = getattr(item_cls, 'sprites', None)
        if sprites is None:
            raise ValueError(f"{item_cls.__name__} has no class-level sprites for inventory items")

        return cls(
            item_id=item_id or definition.item_id,
            item_cls=item_cls,
            game_objects=game_objects,
            sprites=sprites,
            description=definition.description,
            inventory_animation_name=definition.inventory_animation_name,
        )

    def use_item(self):
        use_from_inventory = getattr(self.item_cls, 'use_from_inventory', None)
        if use_from_inventory is None:
            return False
        return use_from_inventory(self)

    def reset_timer(self):
        pass
