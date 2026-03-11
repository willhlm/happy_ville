import math
import random


def sign(num):
    """Return -1 for negative numbers, 1 otherwise."""
    if num < 0:
        return -1
    return 1


class ParticleState:
    """Base class for particle states."""
    
    def __init__(self, particle):
        self.particle = particle
    
    def update(self, dt):
        """Update state logic (non-rendering)."""
        pass
    
    def update_render(self, dt):
        """Update state with rendering logic."""
        pass


class Idle(ParticleState):
    """Standard particle behavior with motion, fading, and lifetime."""
    
    def update_render(self, dt):
        self.particle.motion.update(dt)
        self.particle.fading(dt)
        self.particle.destroy()


class Circle_converge(ParticleState):
    """First phase: particles slow down while moving away from spawn point."""
    
    def __init__(self, particle):
        super().__init__(particle)
        self.time = 200  # Time until transition to next phase
        self.sign = [
            sign(self.particle.velocity[0]),
            sign(self.particle.velocity[1])
        ]
    
    def update_render(self, dt):
        self.time -= dt
        self._update_velocity(dt)
        
        if self.time < 0:
            self.particle.state_manager.transition_to(CircleConvergeToPlayer)
    
    def _update_velocity(self, dt):
        """Slow down velocity based on distance from spawn point."""
        dx = self.particle.true_pos[0] - self.particle.spawn_point[0]
        dy = self.particle.true_pos[1] - self.particle.spawn_point[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Distance-based deceleration
        self.particle.velocity[0] -= 0.001 * distance * self.particle.velocity[0] * dt
        self.particle.velocity[1] -= 0.001 * distance * self.particle.velocity[1] * dt
        
        # Maintain minimum velocity
        self.particle.velocity[0] = self.sign[0] * max(abs(self.particle.velocity[0]), 0.03)
        self.particle.velocity[1] = self.sign[1] * max(abs(self.particle.velocity[1]), 0.03)


class CircleConvergeToPlayer(ParticleState):
    """Second phase: particles converge towards player and create light effect on collision."""
    
    def update_render(self, dt):
        self._update_velocity(dt)
        self._check_collision()
    
    def _check_collision(self):
        """Check if particle has reached player and trigger light effect."""
        if not hasattr(self.particle.game_objects, 'player'):
            return
        
        player_center = self.particle.game_objects.player.hitbox.center
        dx = self.particle.true_pos[0] - player_center[0]
        dy = self.particle.true_pos[1] - player_center[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 5:
            self.particle.game_objects.signals.emit('partilcles_absrobed')
            # Trigger light effect
            if hasattr(self.particle, 'light'):                
                self.particle.light.colour = [1, 1, 1, 1]
                self.particle.light.updates.append(self.particle.light.expand)
                self.particle.light.updates.append(self.particle.light.fade)
                self.particle.light.updates.append(self.particle.light.lifetime)
            
            self.particle.kill()
    
    def _update_velocity(self, dt):
        """Update velocity to move towards player."""
        if not hasattr(self.particle.game_objects, 'player'):
            return
        
        player_center = self.particle.game_objects.player.hitbox.center
        dx = self.particle.true_pos[0] - player_center[0]
        dy = self.particle.true_pos[1] - player_center[1]
        
        # Avoid division by zero
        if dx == 0:
            dx = 0.01
        
        sign_x = sign(dx)
        sign_y = sign(dy)
        
        angle = math.atan(dy / dx)
        
        # Calculate speed based on distance (clamped between 2 and 20)
        speed_x = min(max(abs(dx), 2), 20)
        speed_y = min(max(abs(dy), 2), 20)
        
        # Update velocity towards player
        self.particle.velocity[0] = -sign_x * abs(math.cos(angle)) * dt * speed_x
        self.particle.velocity[1] = -sign_y * abs(math.sin(angle)) * dt * speed_y
    
    def handle_input(self, input):
        """Handle external events."""
        if input == 'light_gone':
            # Called from lights when lifetime < 0
            if hasattr(self.particle.game_objects, 'post_process'):
                if self.particle.game_objects.post_process.shaders.get('glow', False):
                    self.particle.game_objects.post_process.remove_shader('glow')
