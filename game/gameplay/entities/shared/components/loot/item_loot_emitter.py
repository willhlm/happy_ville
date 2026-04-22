import random


class ItemLootEmitterComponent:
    def __init__(self, owner, spawn_velocity=None, spawn_velocity_range=None):
        self.owner = owner
        self.spawn_velocity = spawn_velocity
        self.spawn_velocity_range = spawn_velocity_range or [0, 0]

    def emit_inventory(self, inventory, pos=None, clear=True):
        for item_id, quantity in list(inventory.items()):
            if quantity <= 0:
                continue
            self.emit_item(item_id, quantity=quantity, pos=pos)
            if clear:
                inventory[item_id] = 0

    def emit_item(self, item_id, quantity=1, pos=None, spawn_velocity=None, spawn_velocity_range=None):
        emitted = []
        item_cls = self.owner.game_objects.registry.fetch('items', item_id)
        if item_cls is None:
            raise KeyError(f"Unknown item id: {item_id}")

        for _ in range(quantity):
            item = item_cls(pos or self.owner.hitbox.midtop, self.owner.game_objects)
            self._apply_spawn_impulse(item, spawn_velocity, spawn_velocity_range)
            self._spawn_item(item)
            emitted.append(item)
        return emitted

    def _apply_spawn_impulse(self, item, spawn_velocity=None, spawn_velocity_range=None):
        velocity = self.spawn_velocity if spawn_velocity is None else spawn_velocity
        if velocity is None:
            return

        velocity_range = self.spawn_velocity_range if spawn_velocity_range is None else (spawn_velocity_range or [0, 0])
        item.velocity = [
            random.uniform(velocity[0] - velocity_range[0], velocity[0] + velocity_range[0]),
            random.uniform(velocity[1] - velocity_range[1], velocity[1] + velocity_range[1]),
        ]

    def _spawn_item(self, item):
        item.hitbox.midbottom = (self.owner.hitbox.centerx, self.owner.hitbox.top - 1)
        item.body.update_rect_x()
        item.body.update_rect_y()
        self._resolve_spawn_overlap(item)
        self.owner.game_objects.loot.add(item)

    def _resolve_spawn_overlap(self, item):
        collision_queries = self.owner.game_objects.physics.collision_queries
        platforms = self.owner.game_objects.platforms
        if not collision_queries.sprite_collide_any(item, platforms):
            return

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        step = 5
        max_radius = 200

        original_x, original_y = item.hitbox.topleft
        for dx, dy in directions:
            for radius in range(step, max_radius + step, step):
                item.hitbox.topleft = (original_x + dx * radius, original_y + dy * radius)
                if collision_queries.sprite_collide_any(item, platforms):
                    continue
                item.body.update_rect_x()
                item.body.update_rect_y()
                return

        item.hitbox.topleft = (original_x, original_y)
