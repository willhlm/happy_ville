import pygame
import math
import random
from engine.system import animation
from engine.utils import read_files
from . import states_particles
from .motion import MotionFactory
from .state_manager import StateManager
from .angle_generator import AngleGenerator

class Particles(pygame.sprite.Sprite):
    """Base particle class with composition-based motion and state management."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__()
        self.game_objects = game_objects
        self.spawn_point = [pos[0], pos[1]]
        
        # Particle properties
        self.lifetime = kwarg.get('lifetime', 60)
        self.colour = list(kwarg.get('colour', [255, 255, 255, 255]))
        self.fade_scale = kwarg.get('fade_scale', 1)
        
        # Angle and position setup
        angle_degrees = AngleGenerator.generate(
            dir=kwarg.get('dir', 'isotropic'),
            angle_spread=kwarg.get('angle_spread', [30, 30]),
            angle_dist=kwarg.get('angle_dist', None)
        )
        self.angle = -(2 * math.pi * angle_degrees) / 360
        
        distance = kwarg.get('distance', 0)
        self.true_pos = [
            pos[0] + distance * math.cos(self.angle),
            pos[1] + distance * math.sin(self.angle)
        ]
        
        # Velocity setup
        vel = kwarg.get('vel', {'linear': [7, 15]})
        motion_type = list(vel.keys())[0]
        amp = random.uniform(min(vel[motion_type]), max(vel[motion_type]))
        self.velocity = [-amp * math.cos(self.angle), -amp * math.sin(self.angle)]
        self.phase = random.uniform(-math.pi, math.pi)
        
        # Composition: Motion behavior
        self.gravity_scale = kwarg.get('gravity_scale', 1)
        self.motion = MotionFactory.create(motion_type, self, gravity_scale=self.gravity_scale)
        
        # Composition: State management
        state_name = kwarg.get('state', 'Idle')
        initial_state = getattr(states_particles, state_name)
        self.state_manager = StateManager(self, initial_state)
    
    def update(self, dt):
        """Non-rendering update."""
        pass
    
    def update_render(self, dt):
        """Main update loop with rendering."""
        self._update_position(dt)
        self.lifetime -= dt
        self.state_manager.update_render(dt)
    
    def _update_position(self, dt):
        """Update particle position based on velocity."""
        self.true_pos[0] += self.velocity[0] * dt
        self.true_pos[1] += self.velocity[1] * dt
        self.rect.center = self.true_pos
        self.hitbox.center = self.true_pos
    
    def fading(self, dt):
        """Gradually fade out particle alpha."""
        self.colour[-1] -= self.fade_scale * dt
        self.colour[-1] = max(self.colour[-1], 0)
    
    def destroy(self):
        """Remove particle when lifetime expires."""
        if self.lifetime < 0:
            self.kill()
    
    def draw(self, target):
        """Draw particle with camera offset and shader."""
        camera_scroll = self.game_objects.camera_manager.camera.scroll
        pos = (
            int(self.rect[0] - camera_scroll[0]),
            int(self.rect[1] - camera_scroll[1])
        )
        self.game_objects.game.display.render(
            self.image, target, position=pos, shader=self.shader
        )
    
    def release_texture(self):
        """Hook for texture cleanup."""
        pass


class ShaderParticle(Particles):
    """Base class for particles that use shaders for rendering."""
    
    def __init__(self, pos, game_objects, shader_name, image, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.image = image
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = game_objects.shaders[shader_name]


class Circle(ShaderParticle):
    """Circular particle rendered with circle shader."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, 'circle', Circle.image, **kwarg)
        
        scale = kwarg.get('scale', 3)
        self.radius = random.randint(max(scale - 1, 1), round(scale + 1))
        self.fade_scale = kwarg.get('fade_scale', 2)
        self.gradient = kwarg.get('gradient', 0)
    
    def draw(self, target):
        """Configure shader and draw."""
        self.shader['color'] = self.colour
        self.shader['radius'] = self.radius
        self.shader['gradient'] = self.gradient
        self.shader['size'] = self.image.size
        super().draw(target)
    
    @staticmethod
    def pool(game_objects):
        """Pre-allocate texture for all Circle particles."""
        Circle.image = game_objects.game.display.make_layer((50, 50)).texture


class Goop(ShaderParticle):
    """Distorted circle particle using noise-based shader effects."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, 'goop', Goop.circle, **kwarg)
        
        self.empty = Goop.image2
        self.noise_layer = Goop.image3
        self.fade_scale = 0
        self.time = 0
        
        # Initialize circle texture
        circle_shader = self.game_objects.shaders['circle']
        circle_shader['color'] = kwarg.get('colour', [1, 1, 1, 1])
        circle_shader['radius'] = 6
        circle_shader['size'] = [50, 50]
        circle_shader['gradient'] = kwarg.get('gradient', 0)
        self.game_objects.game.display.render(
            self.empty.texture, Goop.circle, shader=circle_shader
        )
        
        self.image = Goop.circle.texture
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
    
    def update(self, dt):
        super().update(dt)
        self.time += 0.01 * dt
    
    def draw(self, target):
        """Generate noise texture and apply goop shader."""
        # Generate perlin noise
        noise_shader = self.game_objects.shaders['noise_perlin']
        noise_shader['u_resolution'] = self.image.size
        noise_shader['u_time'] = self.time
        noise_shader['scroll'] = self.game_objects.camera_manager.camera.scroll
        noise_shader['scale'] = [10, 10]
        self.game_objects.game.display.render(
            self.empty.texture, self.noise_layer, shader=noise_shader
        )
        
        # Apply goop effect
        self.game_objects.shaders['goop']['TIME'] = self.time
        self.game_objects.shaders['goop']['flowMap'] = self.noise_layer.texture
        super().draw(target)
    
    @staticmethod
    def pool(game_objects):
        """Pre-allocate textures for Goop particles."""
        Goop.image2 = game_objects.game.display.make_layer((50, 50))
        Goop.image3 = game_objects.game.display.make_layer((50, 50))
        Goop.circle = game_objects.game.display.make_layer((50, 50))


class Spark(ShaderParticle):
    """Spark particle with velocity-based rendering."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, 'spark', Spark.image, **kwarg)
        
        self.fade_scale = kwarg.get('fade_scale', 1)
        self.shader['size'] = self.image.size
        self.shader['scale'] = kwarg.get('scale', 1)
    
    def draw(self, target):
        """Configure shader with current velocity and draw."""
        self.shader['colour'] = self.colour
        self.shader['velocity'] = self.velocity
        super().draw(target)
    
    @staticmethod
    def pool(game_objects):
        """Pre-allocate texture for Spark particles."""
        Spark.image = game_objects.game.display.make_layer((50, 50)).texture


class FloatyParticles(Particles):
    """Animated texture-based particles with color shader effects."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        
        self.animation = animation.Animation(self, framerate=0.7)
        self.sprites = FloatyParticles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = self.game_objects.shaders['particles_configure']
        
        # Color configuration
        random_value = random.uniform(0.7, 1)
        self.colour1 = (0, 0.5 * random_value, 1 * random_value, 1)
        self.colour2 = (1, 1, 1, 1)
        self.colour3 = (1, 0, 0, 1)
    
    def update(self, dt):
        self.animation.update(dt)
        self._update_position(dt)
        self._update_velocity(dt)
    
    def _update_velocity(self, dt):
        """Custom velocity update for floaty motion."""
        self.velocity[1] += dt * 0.01
    
    def _update_uniforms(self):
        """Update shader uniforms for rendering."""
        self.shader['colour1'] = self.colour1
        self.shader['colour2'] = self.colour2
        self.shader['colour3'] = self.colour3
        self.shader['normalised_frame'] = self.animation.frame / len(self.sprites['idle'])
    
    def draw(self, target):
        """Update uniforms and draw."""
        self._update_uniforms()
        super().draw(target)
    
    def reset_timer(self):
        """Called when animation finishes."""
        self.kill()
    
    @staticmethod
    def pool(game_objects):
        """Load sprite assets."""
        FloatyParticles.sprites = read_files.load_sprites_dict(
            'assets/sprites/entities/visuals/cosmetics/particles/floaty/',
            game_objects
        )


class Offset(Particles):
    """Particle with sinusoidal offset motion (not fully implemented)."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        
        self.sprites = Offset.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = self.game_objects.shaders['particles_configure']
        
        # Color configuration
        random_value = random.uniform(0.7, 1)
        self.colour1 = (0, 0.5 * random_value, 1 * random_value, 1)
        self.colour2 = (1, 1, 1, 1)
        self.colour3 = (1, 0, 0, 1)
        
        self.time = 0
    
    def update(self, dt):
        self._update_position(dt)
        self._update_velocity()
        self.destroy()
        self.time += dt
        self.lifetime -= dt
    
    def _update_velocity(self):
        """Sinusoidal velocity pattern."""
        self.velocity = [
            math.sin(self.time * 0.1),
            math.sin(self.time * 0.1) - 0.5
        ]
    
    def _update_uniforms(self):
        """Update shader uniforms for rendering."""
        self.shader['colour1'] = self.colour1
        self.shader['colour2'] = self.colour2
        self.shader['colour3'] = self.colour3
        self.shader['normalised_frame'] = self.animation.frame / len(self.sprites['idle'])
    
    def draw(self, target):
        """Update uniforms and draw."""
        self._update_uniforms()
        super().draw(target)
    
    @staticmethod
    def pool(game_objects):
        """Load sprite assets."""
        Offset.sprites = read_files.load_sprites_dict(
            'Sprites/GFX/particles/offset/',
            game_objects
        )
