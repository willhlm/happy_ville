import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity

    def handle_input(self,input,duration=100):
        pass

class Floor(AI):
    def __init__(self, entity, move_direction = [1 ,0], gravity_direction = [0, 1]):
        super().__init__(entity)
        self.move_direction = [move_direction[0] * self.entity.clockwise, move_direction[1]]
        self.gravity_direction = gravity_direction

    def update(self):
        # Apply gravity and movement
        print('floor', self.move_direction, self.gravity_direction)
        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Transition to the wall or falling state
        if self.entity.collision_types['left']:
            if self.move_direction[0] != 1:
                self.entity.AI = LeftWall(self.entity, move_direction = [0, -1], gravity_direction = [-1, 0])
        elif self.entity.collision_types['right']:
            if self.entity.clockwise == 1:#if clockwise            
                self.entity.AI = RightWall(self.entity, move_direction = [0, -1 * self.entity.clockwise], gravity_direction = [1, 0])
        elif not self.entity.collision_types['bottom']:  # Transition to falling when there's no platform below
            self.entity.AI = Falling(self.entity, move_direction = [0, 1], gravity_direction = [-1* self.entity.clockwise, 0])

class RightWall(AI):
    def __init__(self, entity, move_direction, gravity_direction):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction

    def update(self):
        # Apply gravity and movement
        print('right', self.move_direction, self.gravity_direction)
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
                self.entity.AI = Ceiling(self.entity, move_direction=[-1, 0], gravity_direction=[0, -1])
        elif not self.entity.collision_types['right']:  # Transition to falling when there's no platform to the right
          self.entity.AI = Falling(self.entity, move_direction=[1, 0], gravity_direction=[0, 1 * self.entity.clockwise]) 

class LeftWall(AI):
    def __init__(self, entity, move_direction, gravity_direction):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction

    def update(self):
        # Apply gravity and movement
        print('left', self.move_direction, self.gravity_direction)
        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Handle collisions and transitions
        if self.entity.collision_types['top']:
            if self.entity.clockwise == -1:#if count etclockwise
                self.entity.AI = Ceiling(self.entity, move_direction=[1, 0], gravity_direction=[0, -1])
        elif self.entity.collision_types['bottom']:
            if self.entity.clockwise == 1:#if countter clockwise
                self.entity.AI = Floor(self.entity, move_direction=[1, 0], gravity_direction=[0, 1])
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1], gravity_direction=[1, 0])
        elif not self.entity.collision_types['left']:  # Transition to falling when leaving the left wall
            self.entity.AI = Falling(self.entity, move_direction=[-1, 0], gravity_direction=[0, -1 *  self.entity.clockwise])

class Ceiling(AI):
    def __init__(self, entity, move_direction, gravity_direction):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction

    def update(self):
        # Apply gravity and movement
        print('top', self.move_direction, self.gravity_direction)
        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Handle collisions and transitions
        if self.entity.collision_types['left']:  
            if self.entity.clockwise == 1:#if countter clockwise          
                self.entity.AI = LeftWall(self.entity, move_direction=[0, 1 * self.entity.clockwise], gravity_direction=[-1, 0])
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1 * self.entity.clockwise], gravity_direction=[1, 0])
        elif self.entity.collision_types['bottom']:
            self.entity.AI = Floor(self.entity, move_direction=[0, -1], gravity_direction=[1, 0])
        elif not self.entity.collision_types['top']:  # Transition to falling when leaving the ceiling
            self.entity.AI = Falling(self.entity, move_direction=[0, -1], gravity_direction=[1 * self.entity.clockwise, 0])

class Falling(AI):
    def __init__(self, entity, move_direction, gravity_direction):
        super().__init__(entity)
        self.move_direction = move_direction
        self.gravity_direction = gravity_direction

    def update(self):
        # Apply gravity and movement
        print('fall', self.move_direction, self.gravity_direction)
        self.entity.acceleration[0] = self.gravity_direction[0]
        self.entity.acceleration[1] = self.gravity_direction[1]
        self.entity.velocity[0] = self.move_direction[0]
        self.entity.velocity[1] = self.move_direction[1]

        # Check collisions and switch to appropriate states
        if self.entity.collision_types['bottom']:
            self.entity.AI = Floor(self.entity)  # Switch to floor state when touching the ground
        elif self.entity.collision_types['left']:
            self.entity.AI = LeftWall(self.entity, move_direction=[0, 1* self.entity.clockwise], gravity_direction=[-1, 0])
        elif self.entity.collision_types['right']:
            self.entity.AI = RightWall(self.entity, move_direction=[0, -1 * self.entity.clockwise], gravity_direction=[1, 0])
        elif self.entity.collision_types['top']:
            self.entity.AI = Ceiling(self.entity, move_direction=[-1 * self.entity.clockwise, 0], gravity_direction=[0, -1])
