from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.collision.contact_state import ContactState
from gameplay.entities.shared.components.collision.platform_collider import PlatformCollider
from gameplay.entities.shared.modifiers import modifier_movement
from engine import constants as C

class Item(AnimatedEntity):#
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.contact_state = ContactState()
        self.go_through = {'drop_through': True}
        self.velocity = [0, 0]
        self.body = EntityBody(self)
        self.movement_manager = modifier_movement.MovementManager(self)
        self.platform_collider = PlatformCollider(self)
        self.hitstop = HitstopComponent()
        self.description = ''
        
        self.bounce_coefficient = 0.6
        self.bounce_directions = set()  # can contain 'up', 'down', 'left', 'right'
        self.acceleration = C.acceleration_item.copy()
        self.friction = C.friction_item.copy()
        self.max_vel = C.max_vel_item.copy()
        self._movement_context = modifier_movement.MovementContext(self)

    def spawn_position(self):# Make sure the items don't spawn inside the platforms: call it when spawning the loot
        if not self.game_objects.physics.collision_queries.sprite_collide_any(self, self.game_objects.platforms):
            return

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        step = 5
        max_radius = 200

        original_x, original_y = self.hitbox.topleft
        for dx, dy in directions:
            for radius in range(step, max_radius + step, step):
                new_x = original_x + dx * radius
                new_y = original_y + dy * radius
                self.hitbox.topleft = (new_x, new_y)
                if not self.game_objects.physics.collision_queries.sprite_collide_any(self, self.game_objects.platforms):
                    self.body.update_rect_x()
                    self.body.update_rect_y()
                    return
        
        self.hitbox.topleft = (original_x, original_y)# If no space found, put it back to original position

    def update_vel(self, dt):#add gravity
        context = self.movement_manager.resolve()
        self._movement_context = context
        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], context.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.acceleration[0] - context.friction[0] * self.velocity[0]) + context.velocity[0]

    def update(self, dt):
        super().update(dt)
        self.movement_manager.update(dt)
        self.update_vel(dt)

    def attract(self, pos):#the omamori calls on this in loot group
        pass

    def interact(self, player):#when player press T
        pass

    def on_collision(self, entity):#when the player collides with this object
        pass

    def collision(self, entity):#when the player collides with this object
        pass      

    def on_noncollision(self, entity):
        pass    
    
    def release_texture(self):#stuff that have pool shuold call this
        pass

    def apply_ground_snap_velocity(self):
        if self.bounce_coefficient < 0.1:#to avoid falling through one way collisiosn
            self.velocity[1] = max(self.velocity[1],0.6)

    def is_on_floor(self):
        return self.contact_state.is_on_floor()

    def was_on_floor(self):
        return self.contact_state.was_on_floor

    def get_support_body(self):
        return self.contact_state.support_body

    def get_previous_support_body(self):
        return self.contact_state.previous_support_body

    def should_apply_support_motion(self, axis, amount):
        return amount != 0

    def get_support_contact_tolerance(self):
        return 10

    def on_crush(self, block):
        self.kill()

    def set_ui(self):#called from backpask
        pass

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
            self.bounce_directions.add("down" if collision.side == 'bottom' else "up")
            return

        self.bounce_directions.add(collision.side)

    def perform_bounce(self):
        for direction in self.bounce_directions:
            if direction == "down" or direction == "up":
                self.velocity[0] = 0.7 * self.velocity[0] 
                self.velocity[1] = -self.bounce_coefficient * self.velocity[1]                
                self.bounce_coefficient *= self.bounce_coefficient                                
            elif direction == "left" or direction == "right":
                self.velocity[0] *= -1     
