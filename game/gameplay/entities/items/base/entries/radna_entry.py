from .base_entry import ItemEntry


class RadnaEntry(ItemEntry):
    def __init__(self, item_cls, game_objects, description, animation_name, level):
        super().__init__(item_cls, game_objects, description, animation_name)
        self.level = level
        self.equipped_ring = None
        self.shader = None

    @classmethod
    def from_item_class(cls, item_cls, game_objects):
        animation_name = cls._resolve_animation_name(item_cls)
        definition = item_cls.get_item_definition()
        description = definition.description
        level = getattr(item_cls, 'inventory_level', 1)
        return cls(item_cls, game_objects, description, animation_name, level)

    @property
    def owner(self):
        if self.equipped_ring is None:
            return None
        return self.equipped_ring.owner

    def update_equipped(self):
        self.item_cls.entry_update_equipped(self)

    def handle_press_input(self, input):
        self.item_cls.entry_on_handle_press_input(self, input)

    def attach(self):
        self.shader = self.game_objects.shaders['colour']
        self.item_cls.entry_on_attach(self)

    def detach(self):
        self.shader = None
        self.item_cls.entry_on_detach(self)
