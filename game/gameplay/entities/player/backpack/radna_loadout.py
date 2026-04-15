from gameplay.entities.items.base.entries import RingSlot


class RadnaLoadout:
    def __init__(self):
        self.inventory = {}  # {"half_damage": <RadnaEntry>}
        self._available_slots = ['index', 'long', 'ring', 'small']
        self.rings = {finger: RingSlot(finger) for finger in self._available_slots}

    def get_radna(self, item_name):
        return self.inventory.get(item_name, False)

    def get_ring(self, item_name):
        return self.rings.get(item_name, False)

    def add(self, item):
        self.inventory[item.get_item_id()] = item

    def unlock_next_ring(self, item_cls, owner=None, level=1):
        if owner is None:
            return False
        for slot in self._available_slots:
            ring = self.rings[slot]
            if not ring.unlocked:
                ring.unlock(item_cls, owner.game_objects, owner=owner, level=level)
                return True
        return False

    def upgrade_ring(self, finger):
        ring = self.rings.get(finger)
        if not ring:
            return False
        return ring.upgrade()

    def upgrade_next_ring(self):
        for slot in self._available_slots:
            ring = self.rings[slot]
            if ring.unlocked:
                return ring.upgrade()
        return False

    def update(self):
        for ring in self.rings.values():
            ring.update_equipped()

    def handle_press_input(self, input):
        for ring in self.rings.values():
            ring.handle_press_input(input)

    def find_compatible_slot(self, radna):
        for slot in self._available_slots:
            ring = self.rings[slot]
            if ring.can_attach(radna):
                return slot
        return None

    def equip_item(self, radna):
        slot = self.find_compatible_slot(radna)
        if slot:
            self.rings[slot].attach_radna(radna)
            return True
        return False

    def remove_item(self, radna):
        for slot in self._available_slots:
            ring = self.rings[slot]
            if ring.attached_radna == radna:
                ring.detach_radna()
                return True
        return False
