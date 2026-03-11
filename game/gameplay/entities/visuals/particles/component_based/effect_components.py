"""
Effect components - modify particle behavior and appearance.
"""
import math
from .components import Component
from engine.utils.functions import sign

class FadeComponent(Component):
    """Gradually fades particle alpha over time."""
    
    def __init__(self, particle, fade_scale=1):
        super().__init__(particle)
        self.fade_scale = fade_scale
    
    def _update(self, dt):
        self.particle.colour[-1] -= self.fade_scale * dt
        self.particle.colour[-1] = max(self.particle.colour[-1], 0)
        return False

class LifetimeComponent(Component):
    """Handles particle lifetime and destruction."""

    def __init__(self, particle, frames):
        super().__init__(particle)
        self.lifetime = frames

    def _update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.particle.kill()
            return True  # Remove component
        return False

class DecelerationComponent(Component):
    """Slows particle down based on distance from spawn point."""
    
    def __init__(self, particle, decel_factor=0.001, min_velocity=0.03):
        super().__init__(particle)
        self.decel_factor = decel_factor
        self.min_velocity = min_velocity
        self.velocity_sign = [
            sign(particle.velocity[0]),
            sign(particle.velocity[1])
        ]
    
    def _update(self, dt):
        dx = self.particle.true_pos[0] - self.particle.spawn_point[0]
        dy = self.particle.true_pos[1] - self.particle.spawn_point[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Distance-based deceleration
        self.particle.velocity[0] -= self.decel_factor * distance * self.particle.velocity[0] * dt
        self.particle.velocity[1] -= self.decel_factor * distance * self.particle.velocity[1] * dt
        
        # Maintain minimum velocity
        self.particle.velocity[0] = self.velocity_sign[0] * max(abs(self.particle.velocity[0]), self.min_velocity)
        self.particle.velocity[1] = self.velocity_sign[1] * max(abs(self.particle.velocity[1]), self.min_velocity)
        return False


class HomingComponent(Component):
    """Makes particle home towards a target after optional delay."""
    
    def __init__(self, particle, target=None, start_delay=0, speed_min=2, speed_max=20):
        super().__init__(particle)
        self.target = target  # Can be an object with hitbox.center or a [x, y] position
        self.start_delay = start_delay
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.is_active = start_delay <= 0
    
    def _update(self, dt):
        # Wait for delay
        if not self.is_active:
            self.start_delay -= dt
            if self.start_delay <= 0:
                self.is_active = True
            return False
        
        # Get target position
        if self.target is None:
            return False
        
        if hasattr(self.target, 'hitbox'):
            target_pos = self.target.hitbox.center
        elif hasattr(self.target, '__getitem__'):
            target_pos = self.target
        else:
            return False
        
        # Calculate direction to target
        dx = self.particle.true_pos[0] - target_pos[0]
        dy = self.particle.true_pos[1] - target_pos[1]
        
        # Avoid division by zero
        if abs(dx) < 0.01:
            dx = 0.01
        
        sign_x = sign(dx)
        sign_y = sign(dy)
        
        angle = math.atan(dy / dx)
        
        # Calculate speed based on distance (clamped)
        speed_x = min(max(abs(dx), self.speed_min), self.speed_max)
        speed_y = min(max(abs(dy), self.speed_min), self.speed_max)
        
        # Update velocity towards target
        self.particle.velocity[0] = -sign_x * abs(math.cos(angle)) * dt * speed_x
        self.particle.velocity[1] = -sign_y * abs(math.sin(angle)) * dt * speed_y
        
        return False


class CollisionComponent(Component):
    """Detects collision with target and triggers callback."""
    
    def __init__(self, particle, target, collision_distance=5, on_collision=None):
        super().__init__(particle)
        self.target = target
        self.collision_distance = collision_distance
        self.on_collision = on_collision  # Callback function
    
    def _update(self, dt):
        if self.target is None:
            return False
        
        # Get target position
        if hasattr(self.target, 'hitbox'):
            target_pos = self.target.hitbox.center
        elif hasattr(self.target, '__getitem__'):
            target_pos = self.target
        else:
            return False
        
        # Check distance
        dx = self.particle.true_pos[0] - target_pos[0]
        dy = self.particle.true_pos[1] - target_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.collision_distance:
            if self.on_collision:
                self.on_collision(self.particle, self.target)

            return True  # Remove component
        
        return False

class TimedTransitionComponent(Component):
    """Transitions to a different component setup after a delay."""
    
    def __init__(self, particle, delay, on_transition):
        super().__init__(particle)
        self.delay = delay
        self.on_transition = on_transition  # Callback that receives particle
    
    def _update(self, dt):
        self.delay -= dt
        if self.delay <= 0:
            if self.on_transition:
                self.on_transition(self.particle)
            return True  # Remove this component
        return False

#not used
class TrailComponent(Component):
    """Spawns trail particles behind this particle."""
    
    def __init__(self, particle, spawn_interval=5, trail_particle_type=None, trail_kwargs=None):
        super().__init__(particle)
        self.spawn_interval = spawn_interval
        self.time_since_spawn = 0
        self.trail_particle_type = trail_particle_type
        self.trail_kwargs = trail_kwargs or {}
    
    def _update(self, dt):
        self.time_since_spawn += dt
        
        if self.time_since_spawn >= self.spawn_interval:
            self.time_since_spawn = 0
            
            if self.trail_particle_type:
                # Spawn trail particle at current position
                self.trail_particle_type(
                    self.particle.true_pos,
                    self.particle.game_objects,
                    **self.trail_kwargs
                )
        
        return False


class RotationComponent(Component):
    """Rotates the particle over time (for sprites)."""
    
    def __init__(self, particle, rotation_speed=1):
        super().__init__(particle)
        self.rotation_speed = rotation_speed
        self.current_rotation = 0
    
    def _update(self, dt):
        self.current_rotation += self.rotation_speed * dt
        if hasattr(self.particle, 'rotation'):
            self.particle.rotation = self.current_rotation
        return False


class SineWaveComponent(Component):
    """Adds sinusoidal motion perpendicular to velocity."""
    
    def __init__(self, particle, amplitude=1, frequency=0.1):
        super().__init__(particle)
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0
    
    def _update(self, dt):
        self.time += dt
        
        # Calculate perpendicular offset
        offset = self.amplitude * math.sin(self.time * self.frequency)
        
        # Apply perpendicular to velocity
        if self.particle.velocity[0] != 0 or self.particle.velocity[1] != 0:
            # Get perpendicular vector
            vel_mag = math.sqrt(self.particle.velocity[0]**2 + self.particle.velocity[1]**2)
            if vel_mag > 0:
                perp_x = -self.particle.velocity[1] / vel_mag
                perp_y = self.particle.velocity[0] / vel_mag
                
                self.particle.velocity[0] += perp_x * offset * dt
                self.particle.velocity[1] += perp_y * offset * dt
        
        return False

