import math


class Motion:
    """Base class for particle motion behaviors."""
    
    def __init__(self, particle):
        self.particle = particle
    
    def update(self, dt):
        """Update particle velocity based on motion type."""
        pass


class LinearMotion(Motion):
    """Linear motion with gradual deceleration."""
    
    def update(self, dt):
        self.particle.velocity[0] -= 0.01 * self.particle.velocity[0] * dt
        self.particle.velocity[1] -= 0.01 * self.particle.velocity[1] * dt


class GravityMotion(Motion):
    """Gravity-affected motion."""
    
    def __init__(self, particle, gravity_scale=1):
        super().__init__(particle)
        self.gravity_scale = gravity_scale
    
    def update(self, dt):
        self.particle.velocity[1] += dt * self.gravity_scale


class WaveMotion(Motion):
    """Sinusoidal wave motion."""
    
    def __init__(self, particle, gravity_scale=1):
        super().__init__(particle)
        self.gravity_scale = gravity_scale
    
    def update(self, dt):
        time_factor = self.particle.lifetime * 0.1
        angle_phase = self.particle.angle + self.particle.phase
        self.particle.velocity = [
            0.5 * math.sin(time_factor + angle_phase),-self.gravity_scale
        ]


class EjacMotion(Motion):
    """Ejection motion with horizontal damping and vertical settling."""
    
    def __init__(self, particle):
        super().__init__(particle)
        self.end_y_vel = -0.9
    
    def update(self, dt):
        # Horizontal velocity with damping and phase-based oscillation
        self.particle.velocity[0] -= (
            0.065 * self.particle.velocity[0] * dt + 
            0.03 * math.sin(self.particle.phase)
        )
        
        # Vertical velocity settling towards target
        self.particle.velocity[1] += dt * (self.end_y_vel - self.particle.velocity[1]) * 0.1


class MotionFactory:
    """Factory for creating motion instances."""
    
    @staticmethod
    def create(motion_type, particle, **kwargs):
        """
        Create a motion instance based on type.
        
        Args:
            motion_type: String identifier ('linear', 'gravity', 'wave', 'ejac')
            particle: The particle this motion will affect
            **kwargs: Additional parameters (e.g., gravity_scale)
        
        Returns:
            Motion instance
        """
        motion_map = {
            'linear': LinearMotion,
            'gravity': GravityMotion,
            'wave': WaveMotion,
            'ejac': EjacMotion
        }
        
        motion_class = motion_map.get(motion_type, LinearMotion)
        
        # Pass relevant kwargs to motion constructor
        if motion_type in ['gravity', 'wave']:
            return motion_class(particle, kwargs.get('gravity_scale', 1))
        else:
            return motion_class(particle)
