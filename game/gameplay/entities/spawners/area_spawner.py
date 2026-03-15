import pygame
import random
from gameplay.entities.base.static_entity import StaticEntity
from gameplay.entities.projectiles import FallingRock

class PendingStrike:
    def __init__(self, impact_position, spawn_position, timer, warning_window):
        self.impact_position = impact_position
        self.spawn_position = spawn_position
        self.timer = timer
        self.warning_window = warning_window
        self.warning_timer = 0

    def update(self, dt):
        self.timer -= dt
        self.warning_timer -= dt

    def should_warn(self):
        return self.timer > 0 and self.timer <= self.warning_window and self.warning_timer <= 0

    def reset_warning_timer(self, interval):
        self.warning_timer = interval

    def should_spawn(self):
        return self.timer <= 0

class AreaSpawner(StaticEntity):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.game_objects = game_objects
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        
        self.attack_id = kwarg.get('attack_id', 'bjorn_slam')
        self.projectile_count = int(kwarg.get('count', 10))
        self.warning_delay = int(kwarg.get('warning_delay', 40)) #how long the projectile waits to spawn from the warning particles
        self.spawn_height = int(kwarg.get('spawn_height', game_objects.game.window_size[1])) #approximate fall distance below the spawner area
        self.warning_particles = int(kwarg.get('warning_particles', 4))#number
        self.warning_spread = int(kwarg.get('warning_spread', 10))#particle spread
        self.warning_interval = int(kwarg.get('warning_interval', 6))#how often the particle is emmited
        self.offscreen_margin = int(kwarg.get('offscreen_margin', 24))
        self.spawn_mode = kwarg.get('spawn_mode', 'sequential')
        self.spawn_interval = int(kwarg.get('spawn_interval', 40))#interval inbetween the projecitles

        self.burst_size = max(1, int(kwarg.get('burst_size', 3)))
        self.pending_projectiles = []

        self.game_objects.signals.subscribe('fall_projectiles', self.start_falling_projectiles)
            
    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def kill(self):
        self.game_objects.signals.unsubscribe('fall_projectiles', self.start_falling_projectiles)
        super().kill()

    def update(self, dt):
        spawned_projectiles = []
        for pending_strike in self.pending_projectiles:
            pending_strike.update(dt)

            if pending_strike.should_warn():
                self.spawn_warning_particles(pending_strike.spawn_position, pending_strike.impact_position)
                pending_strike.reset_warning_timer(self.warning_interval)

            if pending_strike.should_spawn():
                self.game_objects.eprojectiles.add(FallingRock(pending_strike.spawn_position, self.game_objects))
                spawned_projectiles.append(pending_strike)

        for pending_strike in spawned_projectiles:
            self.pending_projectiles.remove(pending_strike)

    def start_falling_projectiles(self, attack_id=None, count=None, warning_delay=None, **kwargs):
        if attack_id not in (None, self.attack_id):
            return

        projectile_count = int(count) if count is not None else self.projectile_count
        delay = int(warning_delay) if warning_delay is not None else self.warning_delay

        batch_size = self.resolve_batch_size(projectile_count)
        for projectile_index in range(projectile_count):
            impact_position, spawn_position = self.sample_projectile_positions()
            batch_index = projectile_index // batch_size
            timer = delay + batch_index * self.spawn_interval
            self.pending_projectiles.append(PendingStrike(impact_position, spawn_position, timer, delay))

    def resolve_batch_size(self, projectile_count):
        if self.spawn_mode == 'simultaneous':
            return max(1, projectile_count)
        if self.spawn_mode == 'burst':
            return min(projectile_count, self.burst_size)
        return 1

    def sample_projectile_positions(self):
        min_x = self.rect.left
        max_x = max(min_x, self.rect.right - 1)
        min_y = self.rect.top
        max_y = max(min_y, self.rect.bottom - 1)
        spawn_position = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
        camera_top = self.game_objects.camera_manager.camera.scroll[1]
        spawn_position[1] = min(spawn_position[1], camera_top - self.offscreen_margin)
        impact_position = [spawn_position[0], spawn_position[1] + self.spawn_height]
        return impact_position, spawn_position

    def spawn_warning_particles(self, spawn_position, impact_position):
        camera_top = self.game_objects.camera_manager.camera.scroll[1]
        warning_y = max(spawn_position[1], camera_top - 18)

        for _ in range(self.warning_particles):
            particle_position = [
                spawn_position[0] + random.randint(-self.warning_spread, self.warning_spread),
                warning_y - random.randint(0, 10),
            ]
            self.game_objects.particles.emit(
                'falling_debris_warning',
                particle_position,
                n=1,
            )
