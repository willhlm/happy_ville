from gameplay.entities.items.base.entries import DyeEntry, InventoryItem


class Inventory:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.items = {}#{"healthpotion": {"item": <InventoryItem>, "quantity": 3}}
        self.dyes = {}
        self.infinity_stones = {}

    def get_item(self, item_name):
        if item_name in self.items:
            return self.items[item_name]['item']
        return False

    def add_dye(self, dye):
        self.dyes[dye.name] = DyeEntry.from_world_item(dye)

    def get_infinity_stone(self, item_id):
        return self.infinity_stones.get(item_id, False)

    def add_infinity_stone(self, stone):
        self.infinity_stones[stone.get_item_id()] = stone

    def add_item(self, item_id, quantity=1):
        if self.items.get(item_id, False):
            self.items[item_id]["quantity"] += quantity
            return

        item_cls = self.game_objects.registry.fetch('items', item_id)
        inventory_item = InventoryItem.from_item_class(item_cls, self.game_objects, item_id=item_id)
        self.items[item_id] = {"item": inventory_item, "quantity": quantity}

    def remove(self, item_name, quantity=1):
        if item_name not in self.items:
            return
        self.items[item_name]["quantity"] -= quantity
        if self.items[item_name]["quantity"] <= 0:
            del self.items[item_name]

    def get_quantity(self, item_name):#return quantity. If item doesn't exist, return 0
        return self.items.get(item_name, {}).get("quantity", 0)
