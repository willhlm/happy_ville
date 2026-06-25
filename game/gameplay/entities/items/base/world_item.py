from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.collision.contact_state import ContactState
from gameplay.entities.shared.components.collision.platform_collider import PlatformCollider
from gameplay.entities.shared.modifiers import modifier_movement
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager
from engine import constants as C

class WorldItem(AnimatedEntity):
    item_definition = None

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.contact_state = ContactState()
        self.go_through = {'drop_through': True}
        self.velocity = [0, 0]
        self.body = EntityBody(self)
        self.movement_modifier = modifier_movement.MovementManager(self)
        self.platform_collider = PlatformCollider(self)
        self.hitstop = HitstopComponent()

        self.bounce_coefficient = 0.6
        self.bounce_directions = set()
        self.acceleration = C.acceleration_item.copy()
        self.friction = C.friction_item.copy()
        self.max_vel = C.max_vel_item.copy()
        self.shader_state = EntityShaderManager(self)
        self.lifetime_component = None
        self.age = 0
        self.consumed = False

    #item difnition methods
    @classmethod
    def get_item_id(cls):
        item_id = cls.get_item_definition().item_id
        if item_id == '':
            raise ValueError(f"{cls.__name__}.item_definition.item_id must be set")
        return item_id

    @classmethod
    def get_item_definition(cls):
        if cls.item_definition is None:
            raise ValueError(f"{cls.__name__}.item_definition must be set")
        return cls.item_definition

    #update merhods
    def update_vel(self, dt):
        context = self.movement_modifier.resolve()
        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], context.max_vel[1])
        self.velocity[0] += dt * (self.acceleration[0] - context.friction[0] * self.velocity[0]) + context.velocity[0]

    def update(self, dt):
        super().update(dt)
        self.age += dt
        self.movement_modifier.update(dt)
        self.update_vel(dt)
        if self.lifetime_component:
            self.lifetime_component.update(dt)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    #pickup methods
    def pickup(self, player):
        pass

    def try_pickup(self, player):
        if self.consumed:
            return False
        if self.pickup(player) is False:
            return False
        self.consumed = True
        return True

    def start_fade(self, alpha=255, fade_rate=0.9, kill_threshold=10):
        if self.consumed: return            
        self.consumed = True
        self.velocity = [0, 0]
        self.shader_state.enter_state('Alpha', alpha=alpha, fade_rate=fade_rate, kill_threshold=kill_threshold, on_complete=self.kill)

    #collisiona and platform support
    def on_collision(self, entity):
        pass

    def collision(self, entity):
        pass

    def on_noncollision(self, entity):
        pass

    def apply_ground_snap_velocity(self):
        if self.bounce_coefficient < 0.1:
            self.velocity[1] = max(self.velocity[1], 0.6)

    def get_support_contact_tolerance(self):
        return 10

    def on_crush(self, block):
        self.kill()

    def draw(self, target):
        blit_pos = [
            int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]),
            int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1]),
        ]
        self.shader_state.draw(self.image, target, blit_pos, flip=self.dir[0] > 0)

    def post_physics_update(self, dt):
        self.consume_contact_effects()
        self.consume_platform_collisions()
        self.movement_modifier.consume_contact_state()
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

    def release_texture(self):
        pass
