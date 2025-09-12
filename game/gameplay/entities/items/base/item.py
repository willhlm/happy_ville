from gameplay.entities.base.platform_entity import PlatformEntity
from engine import constants as C

class Item(PlatformEntity):#
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.description = ''
        self.bounce_coefficient = 0.6
        self.bounce_directions = set()  # can contain 'up', 'down', 'left', 'right'

    def spawn_position(self):# Make sure the items don't spawn inside the platforms: call it when spawning the loot
        if not self.game_objects.collisions.sprite_collide_any(self, self.game_objects.platforms):
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
                if not self.game_objects.collisions.sprite_collide_any(self, self.game_objects.platforms):
                    self.update_rect_x()
                    self.update_rect_y()
                    return
        
        self.hitbox.topleft = (original_x, original_y)# If no space found, put it back to original position

    def update_vel(self, dt):#add gravity
        self.velocity[1] += 0.3*dt
        self.velocity[1] = min(self.velocity[1],  C.max_vel[1])#set a y max speed#

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)

    def attract(self, pos):#the omamori calls on this in loot group
        pass

    def interact(self, player):#when player press T
        pass

    def player_collision(self, player):#when the player collides with this object
        pass

    def release_texture(self):#stuff that have pool shuold call this
        pass

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.bounce_directions.add("up")

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')
        self.bounce_directions.add("down")

    #plotfprm collisions
    def top_collision(self,block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.bounce_directions.add("up")

    def down_collision(self,block):
        super().down_collision(block)
        self.bounce_directions.add("down")

    def right_collision(self,block, type = 'Wall'):
        super().right_collision(block, type)
        self.bounce_directions.add("right")

    def left_collision(self,block, type = 'Wall'):
        super().left_collision(block, type)
        self.bounce_directions.add("left")

    def limit_y(self):
        if self.bounce_coefficient < 0.1:#to avoid falling through one way collisiosn
            self.velocity[1] = max(self.velocity[1],0.6)

    def set_ui(self):#called from backpask
        pass

    def perform_bounce(self):
        for direction in self.bounce_directions:
            if direction == "down" or direction == "up":
                self.velocity[0] = 0.7 * self.velocity[0] 
                self.velocity[1] = -self.bounce_coefficient * self.velocity[1]                
                self.bounce_coefficient *= self.bounce_coefficient                                
            elif direction == "left" or direction == "right":
                self.velocity[0] *= -1     

