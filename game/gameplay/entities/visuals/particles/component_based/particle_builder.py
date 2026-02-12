"""
Particle builder - fluent API for creating particles with components.
Makes particle creation clean and explicit.
"""
import math
import random
from .angle_generator import AngleGenerator
from .particles import Circle, Spark, Goop
from .motion_components import LinearMotion, GravityMotion, WaveMotion, EjacMotion, OrbitalMotion
from .effect_components import (
    FadeComponent, LifetimeComponent, HomingComponent, 
    CollisionComponent, TrailComponent, DecelerationComponent,
    TimedTransitionComponent, RotationComponent, SineWaveComponent
)

COMPONENT_MAP = {
    'linear': lambda p, k: LinearMotion(p, **k),
    'gravity': lambda p, k: GravityMotion(p, **k),
    'wave': lambda p, k: WaveMotion(p, **k),
    'ejac': lambda p, k: EjacMotion(p, **k),
    'orbital': lambda p, k: OrbitalMotion(p, **k),
    'fade': lambda p, k: FadeComponent(p, **k),
    'lifetime': lambda p, k: LifetimeComponent(p, **k),
    'homing': lambda p, k: HomingComponent(p, **k),
    'collision': lambda p, k: CollisionComponent(p, **k),
    'trail': lambda p, k: TrailComponent(p, **k),
    'deceleration': lambda p, k: DecelerationComponent(p, **k),
    'transition': lambda p, k: TimedTransitionComponent(p, **k),
    'rotation': lambda p, k: RotationComponent(p, **k),
    'sine_wave': lambda p, k: SineWaveComponent(p, **k),
}

class ParticleBuilder:
    """
    Fluent API for building particles.
    
    Usage:
        ParticleBuilder(pos, game_objects)
            .circle(radius=5, colour=[255, 0, 0, 255])
            .velocity(10, 45)  # speed, angle
            .gravity(scale=2)
            .fade(speed=3)
            .lifetime(120)
            .build()
    """
    
    def __init__(self, pos, game_objects):
        self.pos = pos
        self.game_objects = game_objects
        self.particle_type = Circle#default
        self.particle_kwargs = {}
        self.components = []
        self._velocity = [0, 0]
        self._angle_rad = 0.0
    
    # Particle type selection
    def circle(self, radius=None, scale=3, gradient=0, colour=None):
        self.particle_type = Circle
        self.particle_kwargs = {
            'radius': radius,
            'scale': scale,
            'gradient': gradient,
            'colour': colour
        }
        return self
    
    def spark(self, scale=1, colour=None):
        """Create a spark particle."""
        self.particle_type = Spark
        self.particle_kwargs = {'scale': scale, 'colour': colour}
        return self
    
    def goop(self, colour=None, gradient=0):
        """Create a goop particle."""
        self.particle_type = Goop
        self.particle_kwargs = {'colour': colour, 'gradient': gradient}
        return self
    
    # Velocity setup
    def velocity(self, speed, angle_degrees):
        angle_rad = -(2 * math.pi * angle_degrees) / 360
        self._angle_rad = angle_rad
        self._velocity = [
            -speed * math.cos(angle_rad),
            -speed * math.sin(angle_rad)
        ]
        return self
    
    def velocity_random(self, min_speed, max_speed, angle_degrees=None):
        """Set random velocity."""
        speed = random.uniform(min_speed, max_speed)
        if angle_degrees is None:
            angle_degrees = random.uniform(0, 360)
        return self.velocity(speed, angle_degrees)
    
    def velocity_directional(self, min_speed, max_speed, direction='isotropic', angle_spread=[30, 30], angle_dist=None):
        """
        Set velocity using angle generator (like original system).
        
        Args:
            direction: 'isotropic', angle number, or [x, y] direction vector
            angle_spread: [lower, upper] angle variance
            angle_dist: 'normal' for normal distribution
        """        
        
        angle_degrees = AngleGenerator.generate(direction, angle_spread, angle_dist)
        speed = random.uniform(min_speed, max_speed)
        return self.velocity(speed, angle_degrees)
    
    def velocity_towards(self, target_pos, speed):
        """Set velocity towards a target."""
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self._velocity = [(dx/dist) * speed, (dy/dist) * speed]
        return self
    
    def velocity_xy(self, vx, vy):
        """Set velocity directly."""
        self._velocity = [vx, vy]
        return self
    
    def spawn_distance(self, distance, angle_degrees=None):
        """
        Offset spawn position by distance at an angle.
        If angle not specified, uses the velocity angle.
        
        Args:
            distance: Distance to offset from spawn point
            angle_degrees: Angle to offset at (uses velocity angle if None)
        """
        if angle_degrees is None:
            # Use velocity angle if available
            if self._velocity[0] != 0 or self._velocity[1] != 0:
                angle_rad = math.atan2(-self._velocity[1], -self._velocity[0])
            else:
                angle_rad = 0
        else:
            angle_rad = -(2 * math.pi * angle_degrees) / 360
        
        self.pos = [
            self.pos[0] + distance * math.cos(angle_rad),
            self.pos[1] + distance * math.sin(angle_rad)
        ]
        return self
    
    # Motion components
    def linear(self, deceleration=0.01):
        """Add linear motion with deceleration."""
        self.components.append(('linear', {'deceleration': deceleration}))
        return self
    
    def gravity(self, scale=1):
        """Add gravity."""
        self.components.append(('gravity', {'gravity_scale': scale}))
        return self
    
    def wave(self, frequency=0.1, amplitude=0.5, gravity_scale=1):
        """Add wave motion."""
        self.components.append(('wave', {
            'frequency': frequency,
            'amplitude': amplitude,
            'gravity_scale': gravity_scale
        }))
        return self
    
    def ejac(self, end_y_vel=-0.9, damping=0.065):
        """Add ejac motion."""
        self.components.append(('ejac', {
            'end_y_vel': end_y_vel,
            'damping': damping
        }))
        return self
    
    def orbital(self, center=None, radius=50, speed=0.1):
        """Add orbital motion."""
        self.components.append(('orbital', {
            'radius': radius,
            'speed': speed
        }))
        return self
    
    # Effect components
    def fade(self, speed=1):
        """Add fade effect."""
        self.components.append(('fade', {'fade_scale': speed}))
        return self
    
    def lifetime(self, frames):
        """Add lifetime management."""
        self.components.append(('lifetime', {'frames': frames}))
        return self
    
    def homing(self, target, delay=0, speed_min=2, speed_max=20):
        """Add homing behavior."""
        self.components.append(('homing', {
            'target': target,
            'start_delay': delay,
            'speed_min': speed_min,
            'speed_max': speed_max
        }))
        return self
    
    def collision(self, target, distance=5, callback=None):
        """Add collision detection."""
        self.components.append(('collision', {
            'target': target,
            'collision_distance': distance,
            'on_collision': callback
        }))
        return self
    
    def trail(self, interval=5, trail_type=None, **trail_kwargs):
        """Add trail effect."""
        if trail_type is None:
            trail_type = self.particle_type or Circle
        self.components.append(('trail', {
            'spawn_interval': interval,
            'trail_particle_type': trail_type,
            'trail_kwargs': trail_kwargs
        }))
        return self
    
    def deceleration(self, factor=0.001, min_vel=0.03):
        """Add distance-based deceleration."""
        self.components.append(('deceleration', {
            'decel_factor': factor,
            'min_velocity': min_vel
        }))
        return self
    
    def transition(self, delay, callback):
        """Add timed transition."""
        self.components.append(('transition', {
            'delay': delay,
            'on_transition': callback
        }))
        return self
    
    def rotation(self, speed=1):
        """Add rotation."""
        self.components.append(('rotation', {'rotation_speed': speed}))
        return self
    
    def sine_wave(self, amplitude=1, frequency=0.1):
        """Add sine wave motion."""
        self.components.append(('sine_wave', {
            'amplitude': amplitude,
            'frequency': frequency
        }))
        return self
    
    def build(self):
        """Build and return the particle."""        
        # Create particle
        particle = self.particle_type(self.pos, self.game_objects, **self.particle_kwargs)
        
        # Set velocity
        particle.velocity = self._velocity
        
        # Add components
        for component_type, kwargs in self.components:
            component = self._create_component(component_type, particle, kwargs)            
            particle.add_component(component)
        
        return particle
    
    def _create_component(self, comp_type, particle, kwargs):
        """Create a component instance."""        
        factory = COMPONENT_MAP.get(comp_type)            
        return factory(particle, kwargs)

