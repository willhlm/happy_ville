from engine.system.animation import Animation


class ItemEntry:
    def __init__(self, item_cls, game_objects, description, animation_name):
        self.item_cls = item_cls
        self.game_objects = game_objects
        self.item_id = item_cls.get_item_id()
        self.sprites = item_cls.sprites
        self.description = description
        self.image = self.sprites[animation_name][0]
        self.animation = Animation(self, animation_name=animation_name)

    @classmethod
    def _resolve_animation_name(cls, item_cls):
        definition = item_cls.get_item_definition()
        animation_name = definition.inventory_animation_name
        if animation_name not in item_cls.sprites:
            return 'idle'
        return animation_name

    def reset_timer(self):
        pass

    def get_item_id(self):
        return self.item_id
