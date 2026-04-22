from engine.system.animation import Animation


class RingSlot:
    def __init__(self, finger):
        self.finger = finger
        self.item_cls = None
        self.game_objects = None
        self.item_id = None
        self.sprites = None
        self.description = ''
        self.image = None
        self.animation = None
        self.owner = None
        self.level = 0
        self.attached_radna = None
        self.unlocked = False

    @property
    def is_equipped(self):
        return self.attached_radna is not None

    def get_item_id(self):
        return self.item_id

    def unlock(self, item_cls, game_objects, owner=None, level=1):
        definition = item_cls.get_item_definition()
        self.item_cls = item_cls
        self.game_objects = game_objects
        self.item_id = item_cls.get_item_id()
        self.sprites = item_cls.sprites
        self.description = definition.description
        self.owner = owner
        self.level = level
        self.unlocked = True
        self.animation = Animation(self, animation_name='idle')
        self.animation.play(f'{self.finger}_{self.level}')
        self.image = self.sprites[self.animation.animation_name][0]

    def can_attach(self, radna):
        return self.unlocked and self.level >= radna.level and self.attached_radna is None

    def update_equipped(self):
        if self.attached_radna:
            self.attached_radna.update_equipped()

    def handle_press_input(self, input):
        if self.attached_radna:
            self.attached_radna.handle_press_input(input)

    def upgrade(self):
        if not self.unlocked:
            return False
        self.level += 1
        self.animation.play(f'{self.finger}_{self.level}')
        return True

    def attach_radna(self, radna):
        self.attached_radna = radna
        self.attached_radna.equipped_ring = self
        self.attached_radna.attach()

    def detach_radna(self):
        if not self.attached_radna:
            return
        self.attached_radna.detach()
        self.attached_radna.equipped_ring = None
        self.attached_radna = None

    def reset_timer(self):
        pass
