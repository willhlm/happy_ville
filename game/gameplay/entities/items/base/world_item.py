from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.collision.contact_state import ContactState
from gameplay.entities.shared.components.collision.platform_collider import PlatformCollider
from gameplay.entities.shared.modifiers import modifier_movement
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.components import PickupComponent
from engine import constants as C


class WorldItem(AnimatedEntity):
    item_definition = None
    pickup_component_cls = PickupComponent
    magnet_delay = 0

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.contact_state = ContactState()
        self.go_through = {'drop_through': True}
        self.velocity = [0, 0]
        self.body = EntityBody(self)
        self.movement_manager = modifier_movement.MovementManager(self)
        self.platform_collider = PlatformCollider(self)
        self.hitstop = HitstopComponent()
        self._description_override = None

        self.bounce_coefficient = 0.6
        self.bounce_directions = set()
        self.acceleration = C.acceleration_item.copy()
        self.friction = C.friction_item.copy()
        self.max_vel = C.max_vel_item.copy()
        self._movement_context = modifier_movement.MovementContext(self)
        self.pickup_component = self.pickup_component_cls()
        self.interact_component = None
        self.lifetime_component = None
        self.age = 0

    @classmethod
    def get_item_id(cls):
        return cls.get_item_definition().item_id

    @classmethod
    def _build_default_item_id(cls):
        chars = []
        for index, char in enumerate(cls.__name__):
            if char.isupper() and index > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)

    @classmethod
    def get_item_definition(cls):
        if cls.item_definition is not None:
            return cls.item_definition

        return ItemDefinition(item_id=cls._build_default_item_id())

    @property
    def description(self):
        if self._description_override is not None:
            return self._description_override
        return self.get_item_definition().description

    @description.setter
    def description(self, value):
        self._description_override = value

    def update_vel(self, dt):
        context = self.movement_manager.resolve()
        self._movement_context = context
        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], context.max_vel[1])
        self.velocity[0] += dt * (self.acceleration[0] - context.friction[0] * self.velocity[0]) + context.velocity[0]

    def update(self, dt):
        super().update(dt)
        self.age += dt
        self.movement_manager.update(dt)
        self.update_vel(dt)
        if self.lifetime_component:
            self.lifetime_component.update(dt)

    def interact(self, player):
        self.pickup_component.interact(self, player)

    def on_collision(self, entity):
        self.pickup_component.on_collision(self, entity)

    def collision(self, entity):
        pass

    def on_noncollision(self, entity):
        pass

    def release_texture(self):
        pass

    def apply_ground_snap_velocity(self):
        if self.bounce_coefficient < 0.1:
            self.velocity[1] = max(self.velocity[1], 0.6)

    def should_apply_support_motion(self, axis, amount):
        return amount != 0

    def get_support_contact_tolerance(self):
        return 10

    def on_crush(self, block):
        self.kill()

    @classmethod
    def pool(cls, game_objects):
        pass

    def get_pickup_persistence_key(self):
        definition = self.get_item_definition()
        return definition.pickup_persistence_key or definition.item_id

    def mark_picked_up(self):
        self.game_objects.world_state.objects.set_bool(
            self.game_objects.map.biome_room_name,
            'interactable_items',
            self.get_pickup_persistence_key(),
            True,
        )

    def kill(self):
        super().kill()
        if self.interact_component:
            self.interact_component.on_kill()

    def post_physics_update(self, dt):
        self.consume_contact_effects()
        self.consume_platform_collisions()
        self.movement_manager.consume_contact_state()
        self.perform_bounce()
        self.bounce_directions.clear()

    def consume_contact_effects(self):
        for collision in self.contact_state.collisions:
            collision.contact_effect.apply(self)

    def consume_platform_collisions(self):
        for collision in self.contact_state.collisions:
            self.handle_platform_collision(collision)

    def handle_platform_collision(self, collision):
        if collision.axis == 'y':
            if collision.side != 'bottom':
                self.velocity[1] = 0
            self.bounce_directions.add('down' if collision.side == 'bottom' else 'up')
            return

        self.bounce_directions.add(collision.side)

    def perform_bounce(self):
        for direction in self.bounce_directions:
            if direction == 'down' or direction == 'up':
                self.velocity[0] = 0.7 * self.velocity[0]
                self.velocity[1] = -self.bounce_coefficient * self.velocity[1]
                self.bounce_coefficient *= self.bounce_coefficient
            elif direction == 'left' or direction == 'right':
                self.velocity[0] *= -1
