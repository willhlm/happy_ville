"""
Component-based particle system.
Particles are pure data + position. Components handle all behavior.
"""
import pygame, random, math
from engine.system import animation
from engine.utils import read_files

class Particle(pygame.sprite.Sprite):
    """
    Base particle class - just data and rendering.
    All behavior is handled by components.
    """
    
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__()
        self.game_objects = game_objects
        
        # Position
        self.spawn_point = [pos[0], pos[1]]
        self.true_pos = [pos[0], pos[1]]
        self.velocity = [0, 0]
        
        # Visual properties
        self.colour = list(kwargs.get('colour', [255, 255, 255, 255]))
                
        # Physics properties (used by some components)
        self.phase = random.uniform(-math.pi, math.pi)
        
        # Component system
        self.components = []
    
    def add_component(self, component):
        """Add a component to this particle."""
        self.components.append(component)
        component.on_add()
        return component
    
    def remove_component(self, component):
        """Remove a component from this particle."""
        if component in self.components:
            component.on_remove()
            self.components.remove(component)
    
    def get_component(self, component_type):
        """Get first component of specific type."""
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp
        return None
    
    def update_position(self, dt):
        """Update position based on velocity."""
        self.true_pos[0] += self.velocity[0] * dt
        self.true_pos[1] += self.velocity[1] * dt
        self.rect.center = self.true_pos
        self.hitbox.center = self.true_pos
    
    def update_render(self, dt):
        self.update_position(dt)
        self.update_components(dt)

    def update_components(self, dt):
        components_to_remove = []
        for component in self.components:
            if component.update(dt):
                components_to_remove.append(component)

        for component in components_to_remove:
            self.remove_component(component)

    def update(self, dt):
        pass
    
    def draw(self, target):
        """Draw particle with camera offset."""       
        camera_scroll = self.game_objects.camera_manager.camera.scroll
        pos = (int(self.rect[0] - camera_scroll[0]), int(self.rect[1] - camera_scroll[1]))        
        self.game_objects.game.display.render(self.image, target, position=pos, shader=self.shader)

class ShaderParticle(Particle):
    """Particle that uses a shader for rendering."""    
    def __init__(self, pos, game_objects, shader_name, image, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.image = image
        self.rect = pygame.Rect(0, 0, image.width, image.height)
        self.rect.center = self.true_pos
        self.hitbox = self.rect.copy()
        self.shader = game_objects.shaders[shader_name]

class Circle(ShaderParticle):
    """Circular particle rendered with circle shader."""        
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, 'circle', Circle.image, **kwarg)
        scale = kwarg.get('scale', 3)
        self.radius = random.randint(max(scale - 1, 1), round(scale + 1))
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
        """Initialize shared texture."""
        Circle.image = game_objects.game.display.make_layer((50, 50)).texture

class Spark(ShaderParticle):
    """Spark particle with velocity-based rendering."""
    
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, 'spark', Spark.image, **kwarg)
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

class SpriteParticle(Particle):
    """Particle that uses sprite textures."""
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
    
    def update(self, dt):
        self.animation.update(dt)
        super().update(dt)

class FloatyParticles(SpriteParticle):
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

class Offset(SpriteParticle):
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
