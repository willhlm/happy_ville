class WallStickPhysics:
    """Handles gravity rotation and wall-sticking physics"""
    
    def __init__(self, entity, clockwise=1):
        self.entity = entity
        self.clockwise = clockwise
        self.surface = 'floor'
        self.target_angle = 0
        self.rotation_speed = 10
        
    def update(self, dt):
        """Update physics - call this every frame"""
        self._check_surface_transitions()
        self._rotate_towards_target()
        self._apply_surface_movement()
        
    def _rotate_towards_target(self):
        """Smoothly rotate sprite"""
        diff = self.target_angle - self.entity.angle
        if abs(diff) > 0:
            step = self.rotation_speed if diff > 0 else -self.rotation_speed
            if abs(diff) < abs(step):
                self.entity.angle = self.target_angle
            else:
                self.entity.angle += step
    
    def _apply_surface_movement(self):
        """Set velocity and gravity based on surface"""
        col = self.entity.collision_types
        
        if self.surface == 'floor':
            self.entity.acceleration = [0, 1]
            # Movement handled by AI states
            
        elif self.surface == 'right_wall':
            self.entity.acceleration = [1, 0]
            # Movement is vertical on walls
            
        elif self.surface == 'left_wall':
            self.entity.acceleration = [-1, 0]
            
        elif self.surface == 'ceiling':
            self.entity.acceleration = [0, -1]
            
        elif self.surface == 'falling':
            # Set gravity based on last surface
            self.entity.acceleration = [0, 1]
            
    def _check_surface_transitions(self):
        """Check collisions and transition surfaces"""
        col = self.entity.collision_types
        
        if self.surface == 'floor':
            if col['left'] and self.clockwise == -1:
                self.surface = 'left_wall'
                self.target_angle = 90
            elif col['right'] and self.clockwise == 1:
                self.surface = 'right_wall'
                self.target_angle = -90
            elif not col['bottom']:
                self.surface = 'falling'
                
        elif self.surface == 'right_wall':
            if col['bottom'] and self.clockwise == -1:
                self.surface = 'floor'
                self.target_angle = 0
            elif col['top'] and self.clockwise == 1:
                self.surface = 'ceiling'
                self.target_angle = 180
            elif not col['right']:
                self.surface = 'falling'
                
        elif self.surface == 'left_wall':
            if col['top'] and self.clockwise == -1:
                self.surface = 'ceiling'
                self.target_angle = 180
            elif col['bottom'] and self.clockwise == 1:
                self.surface = 'floor'
                self.target_angle = 0
            elif not col['left']:
                self.surface = 'falling'
                
        elif self.surface == 'ceiling':
            if col['left'] and self.clockwise == 1:
                self.surface = 'left_wall'
                self.target_angle = 90
            elif col['right'] and self.clockwise == -1:
                self.surface = 'right_wall'
                self.target_angle = -90
            elif not col['top']:
                self.surface = 'falling'
                
        elif self.surface == 'falling':
            if col['bottom']:
                self.surface = 'floor'
                self.target_angle = 0
            elif col['left']:
                self.surface = 'left_wall'
                self.target_angle = 90
            elif col['right']:
                self.surface = 'right_wall'
                self.target_angle = -90
            elif col['top']:
                self.surface = 'ceiling'
                self.target_angle = 180
                
    def get_move_direction(self):
        """Get direction vector for movement"""
        directions = {
            'floor': [self.clockwise, 0],
            'ceiling': [-self.clockwise, 0],
            'left_wall': [0, -1],
            'right_wall': [0, -self.clockwise],
            'falling': [0, 1]
        }
        return directions.get(self.surface, [0, 0])