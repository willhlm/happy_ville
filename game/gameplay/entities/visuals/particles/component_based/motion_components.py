"""
Motion components - define how particles move through space.
"""
import math
from .components import Component

class MotionComponent(Component):
    """Base class for motion components."""
    pass

class LinearMotion(MotionComponent):
    """Linear motion with gradual deceleration."""
    
    def __init__(self, particle, deceleration=0.01):
        super().__init__(particle)
        self.deceleration = deceleration
    
    def _update(self, dt):
        self.particle.velocity[0] -= self.deceleration * self.particle.velocity[0] * dt
        self.particle.velocity[1] -= self.deceleration * self.particle.velocity[1] * dt
        return False

class GravityMotion(MotionComponent):
    """Gravity-affected motion."""
    
    def __init__(self, particle, gravity_scale=1):
        super().__init__(particle)
        self.gravity_scale = gravity_scale
    
    def _update(self, dt):
        self.particle.velocity[1] += dt * self.gravity_scale
        return False

class WaveMotion(MotionComponent):
    """Sinusoidal wave motion."""
    
    def __init__(self, particle, gravity_scale=1, frequency=0.1, amplitude=0.5):
        super().__init__(particle)
        self.gravity_scale = gravity_scale
        self.frequency = frequency
        self.amplitude = amplitude
        self.time = 0
    
    def _update(self, dt):
        self.time += dt
        time_factor = self.time * self.frequency
        angle_phase = self.particle.angle + self.particle.phase
        self.particle.velocity = [
            self.amplitude * math.sin(time_factor + angle_phase),
            -self.gravity_scale
        ]
        return False


class EjacMotion(MotionComponent):
    """Ejection motion with horizontal damping and vertical settling."""
    
    def __init__(self, particle, end_y_vel=-0.9, damping=0.065, oscillation=0.03):
        super().__init__(particle)
        self.end_y_vel = end_y_vel
        self.damping = damping
        self.oscillation = oscillation
    
    def _update(self, dt):
        # Horizontal velocity with damping and phase-based oscillation
        self.particle.velocity[0] -= (
            self.damping * self.particle.velocity[0] * dt + 
            self.oscillation * math.sin(self.particle.phase)
        )
        
        # Vertical velocity settling towards target
        self.particle.velocity[1] += dt * (self.end_y_vel - self.particle.velocity[1]) * 0.1
        return False


class OrbitalMotion(MotionComponent):
    """Circular orbital motion around spawn point."""
    
    def __init__(self, particle, radius=50, speed=0.1):
        super().__init__(particle)
        self.radius = radius
        self.speed = speed
        self.angle = 0
    
    def _update(self, dt):
        self.angle += self.speed * dt
        center_x = self.particle.spawn_point[0]
        center_y = self.particle.spawn_point[1]
        
        # Calculate target position
        target_x = center_x + math.cos(self.angle) * self.radius
        target_y = center_y + math.sin(self.angle) * self.radius
        
        # Set velocity to reach target
        self.particle.velocity[0] = (target_x - self.particle.true_pos[0]) * 0.1
        self.particle.velocity[1] = (target_y - self.particle.true_pos[1]) * 0.1
        return False