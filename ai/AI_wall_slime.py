class AI():
    def __init__(self,entity):
        self.entity = entity

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        pass

class Floor(AI):
    def __init__(self, entity, move_direction = [1 ,0], gravity_direction = [0, 1], sign = 1):
        super().__init__(entity)
        self.move_direction = [move_direction[0] * self.entity.clockwise, move_direction[1]]
        self.gravity_direction = gravity_direction
        self.target_angle = 0
        self.sign = sign

    def update(self):
        self.entity.angle += 10 * self.sign
        if self.sign == 1:
            self.entity.angle = min(self.entity.angle, self.target_angle)
        else:
            self.entity.angle = max(self.entity.angle, self.target_angle) 

        self.entity.acceleration[0] = self.gravity_direction[0]#these stuff needs to be applied before update_vel()
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Transition to the wall or falling state        
        if self.entity.collision_types['left']:
            if self.move_direction[0] != 1:
                self.entity.AI = LeftWall(self.entity, move_direction = [0, -1], gravity_direction = [-1, 0], sign = 1)
        elif self.entity.collision_types['right']:
            if self.entity.clockwise == 1:#if clockwise            
                self.entity.AI = RightWall(self.entity, move_direction = [0, -1 * self.entity.clockwise], gravity_direction = [1, 0], sign = -1)
        elif not self.entity.collision_types['bottom']:  # Transition to falling when there's no platform below
            self.entity.AI = Falling(self.entity, move_direction = [0, 1], gravity_direction = [-1* self.entity.clockwise, 0], sign = 1* self.entity.clockwise)

class RightWall(AI):
    def __init__(self, entity, move_direction, gravity_direction, sign):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction        
        self.target_angle = -90
        self.sign = sign

    def update(self):
        self.entity.angle += 10 * self.sign
        if self.sign == 1:
            self.entity.angle = min(self.entity.angle, self.target_angle)
        else:
            self.entity.angle = max(self.entity.angle, self.target_angle)

        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Handle movement on the wall
        if self.entity.collision_types['bottom']:
            if self.entity.clockwise == -1:#if countter clockwise
                self.entity.AI = Floor(self.entity, move_direction=[1, 0], gravity_direction=[0, 1])                     
        elif self.entity.collision_types['top']:
            if self.entity.clockwise == 1:#if clockwise
                self.entity.AI = Ceiling(self.entity, move_direction=[-1, 0], gravity_direction=[0, -1], sign = -1)
        elif not self.entity.collision_types['right']:  # Transition to falling when there's no platform to the right
          self.entity.AI = Falling(self.entity, move_direction=[1, 0], gravity_direction=[0, 1 * self.entity.clockwise], sign = 1 * self.entity.clockwise) 

class LeftWall(AI):
    def __init__(self, entity, move_direction, gravity_direction, sign):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction
        self.target_angle = 90
        self.sign = sign

    def update(self):
        self.entity.angle += 10 * self.sign

        if self.sign == 1:
            self.entity.angle = min(self.entity.angle, self.target_angle)
        else:
            self.entity.angle = max(self.entity.angle, self.target_angle) 

        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Handle collisions and transitions
        if self.entity.collision_types['top']:
            if self.entity.clockwise == -1:#if count etclockwise
                self.entity.AI = Ceiling(self.entity, move_direction=[1, 0], gravity_direction=[0, -1], sign = 1)
        elif self.entity.collision_types['bottom']:
            if self.entity.clockwise == 1:#if countter clockwise
                self.entity.AI = Floor(self.entity, move_direction=[1, 0], gravity_direction=[0, 1], sign = -1)
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1], gravity_direction=[1, 0])
        elif not self.entity.collision_types['left']:  # Transition to falling when leaving the left wall
            self.entity.AI = Falling(self.entity, move_direction=[-1, 0], gravity_direction=[0, -1 *  self.entity.clockwise], sign = 1 *  self.entity.clockwise)

class Ceiling(AI):
    def __init__(self, entity, move_direction, gravity_direction, sign):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction
        self.target_angle = 180 * sign
        self.sign = sign

    def update(self):
        self.entity.angle += 10 * self.sign
        if self.sign == 1:
            self.entity.angle = min(self.entity.angle, self.target_angle)
        else:
            self.entity.angle = max(self.entity.angle, self.target_angle) 

        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Handle collisions and transitions
        if self.entity.collision_types['left']:  
            if self.entity.clockwise == 1:#if countter clockwise          
                self.entity.AI = LeftWall(self.entity, move_direction=[0, 1 * self.entity.clockwise], gravity_direction=[-1, 0], sign = -1)
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1 * self.entity.clockwise], gravity_direction=[1, 0], sign = 1)            
        elif self.entity.collision_types['bottom']:
            self.entity.AI = Floor(self.entity, move_direction=[0, -1], gravity_direction=[1, 0])
        elif not self.entity.collision_types['top']:  # Transition to falling when leaving the ceiling
            self.entity.AI = Falling(self.entity, move_direction=[0, -1], gravity_direction=[1 * self.entity.clockwise, 0], sign = 1* self.entity.clockwise)
            self.entity.angle = -180 * self.entity.clockwise#flip to the other side
        
class Falling(AI):
    def __init__(self, entity, move_direction, gravity_direction, sign = 1):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction        
        self.sign = sign

    def update(self):
        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Check collisions and switch to appropriate states
        if self.entity.collision_types['bottom']:
            self.entity.AI = Floor(self.entity, sign = self.sign)  # Switch to floor state when touching the ground
        elif self.entity.collision_types['left']:
            self.entity.AI = LeftWall(self.entity, move_direction=[0, 1* self.entity.clockwise], gravity_direction=[-1, 0], sign = self.sign)   
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1 * self.entity.clockwise], gravity_direction=[1, 0], sign = self.sign)
        elif self.entity.collision_types['top']:
            self.entity.AI = Ceiling(self.entity, move_direction=[-1 * self.entity.clockwise, 0], gravity_direction=[0, -1], sign = self.sign)
