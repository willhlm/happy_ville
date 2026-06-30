import pygame
import random
from .pending_spawn import PendingSpawn

class AreaSpawner:
    def __init__(self, pos, game_objects, size, **kwargs):
        self.game_objects = game_objects
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()

        self.spawn_id = kwargs['spawn_id']#required uid set in tiled
        self.projectile_id = kwargs['projectile_id']#set in tiled

        #optional set in tiled with defaults
        self.default_count = int(kwargs.get('count', 10))
        self.warning_delay = int(kwargs.get('warning_delay', 40))
        self.spawn_height = int(kwargs.get('spawn_height', game_objects.game.window_size[1]))
        self.warning_particles = int(kwargs.get('warning_particles', 4))
        self.warning_spread = int(kwargs.get('warning_spread', 10))
        self.warning_interval = int(kwargs.get('warning_interval', 6))
        self.offscreen_margin = int(kwargs.get('offscreen_margin', 24))
        self.spawn_mode = kwargs.get('spawn_mode', 'sequential')
        self.spawn_interval = int(kwargs.get('spawn_interval', 40))
        self.burst_size = max(1, int(kwargs.get('burst_size', 3)))
        self.use_warning_particles = bool(kwargs.get('use_warning_particles', True))
        self.warning_particle_type = kwargs.get('warning_particle_type', 'falling_debris_warning')


        self.pending_spawns = []
        self._next_request_id = 1

        self.game_objects.areas.register_spawner(self)

    def kill(self):
        self.game_objects.areas.unregister_spawner(self)

    def cancel_pending_spawns(self, request_id):
        self.pending_spawns = [
            pending_spawn for pending_spawn in self.pending_spawns
            if pending_spawn.request_id != request_id
        ]

    def update(self, dt):
        completed_spawns = []
        for pending_spawn in self.pending_spawns:
            pending_spawn.update(dt)

            if pending_spawn.should_warn():
                pending_spawn.warning_callback(pending_spawn.spawn_position, pending_spawn.impact_position)
                pending_spawn.reset_warning_timer()

            if pending_spawn.should_spawn():
                pending_spawn.spawn_callback(pending_spawn.spawn_position, pending_spawn.impact_position)
                completed_spawns.append(pending_spawn)

        for pending_spawn in completed_spawns:
            self.pending_spawns.remove(pending_spawn)

    def request_spawns(
        self,
        count,
        spawn_callback,
        spawn_position_callback,
        warning_delay=None,
        warning_interval=None,
        spawn_interval=None,
        warning_callback=None,
    ):
        projectile_count = self.default_count if count is None else int(count)
        delay = int(warning_delay) if warning_delay is not None else self.warning_delay
        resolved_warning_interval = int(warning_interval) if warning_interval is not None else self.warning_interval
        resolved_spawn_interval = int(spawn_interval) if spawn_interval is not None else self.spawn_interval
        batch_size = self.resolve_batch_size(projectile_count)
        request_id = self._next_request_id
        self._next_request_id += 1

        for projectile_index in range(projectile_count):
            impact_position, spawn_position = spawn_position_callback()
            batch_index = projectile_index // batch_size
            timer = delay + batch_index * resolved_spawn_interval
            self.pending_spawns.append(
                PendingSpawn(
                    spawn_position=spawn_position,
                    impact_position=impact_position,
                    timer=timer,
                    warning_window=delay,
                    warning_interval=resolved_warning_interval,
                    warning_callback=warning_callback,
                    spawn_callback=spawn_callback,
                    request_id=request_id,
                )
            )

        return request_id

    def request_projectile_spawns(
        self,
        count=None,
        projectile_id=None,
        projectile_kwargs=None,
        warning_delay=None,
        warning_interval=None,
        spawn_interval=None,
        warning_callback=None,
        spawn_origin='area',
        target_mode='random',
        target_offset=0,
        warning_particle_type=None,
    ):
        resolved_projectile_id = projectile_id or self.projectile_id
        resolved_warning_callback = warning_callback
        if resolved_warning_callback is None and self.use_warning_particles:
            resolved_warning_callback = lambda spawn_position, impact_position: self.spawn_warning_particles(
                spawn_position,
                impact_position,
                particle_type=warning_particle_type,
            )

        return self.request_spawns(
            count=count,
            spawn_callback=lambda spawn_position, impact_position: self.spawn_projectile(
                resolved_projectile_id,
                spawn_position,
                impact_position,
                projectile_kwargs=projectile_kwargs,
            ),
            spawn_position_callback=lambda: self.sample_spawn_positions(
                spawn_origin=spawn_origin,
                target_mode=target_mode,
                target_offset=target_offset,
            ),
            warning_delay=warning_delay,
            warning_interval=warning_interval,
            spawn_interval=spawn_interval,
            warning_callback=resolved_warning_callback,
        )

    def resolve_batch_size(self, projectile_count):
        if self.spawn_mode == 'simultaneous':
            return max(1, projectile_count)
        if self.spawn_mode == 'burst':
            return min(projectile_count, self.burst_size)
        return 1

    def sample_spawn_position(self):
        min_x = self.rect.left
        max_x = max(min_x, self.rect.right - 1)
        min_y = self.rect.top
        max_y = max(min_y, self.rect.bottom - 1)
        return [random.randint(min_x, max_x), random.randint(min_y, max_y)]

    def sample_spawn_position_near(self, anchor_x, max_offset):
        min_x = max(self.rect.left, int(anchor_x - max_offset))
        max_x = min(self.rect.right - 1, int(anchor_x + max_offset))
        if min_x > max_x:
            # If the target is outside this spawner's horizontal coverage,
            # snap to the nearest valid x instead of failing the spawn request.
            clamped_x = max(self.rect.left, min(self.rect.right - 1, int(anchor_x)))
            min_x = clamped_x
            max_x = clamped_x

        min_y = self.rect.top
        max_y = max(min_y, self.rect.bottom - 1)
        return [random.randint(min_x, max_x), random.randint(min_y, max_y)]

    def sample_spawn_positions(self, spawn_origin='area', target_mode='random', target_offset=0):
        spawn_position = self._sample_targeted_position(target_mode=target_mode, target_offset=target_offset)

        if spawn_origin == 'offscreen':
            camera_top = self.game_objects.camera_manager.camera.scroll[1]
            spawn_position[1] = min(spawn_position[1], camera_top - self.offscreen_margin)
            impact_position = [spawn_position[0], spawn_position[1] + self.spawn_height]
        elif spawn_origin == 'area':
            impact_position = spawn_position.copy()
        else:
            raise ValueError(f"AreaSpawner {self.spawn_id} has unsupported spawn_origin '{spawn_origin}'")

        return impact_position, spawn_position

    def _sample_targeted_position(self, target_mode='random', target_offset=0):
        if target_mode == 'random':
            return self.sample_spawn_position()
        if target_mode == 'player_x':
            return self.sample_spawn_position_near(self.game_objects.player.hitbox.centerx, target_offset)
        if target_mode == 'center_x':
            return self.sample_spawn_position_near(self.rect.centerx, target_offset)
        raise ValueError(f"AreaSpawner {self.spawn_id} has unsupported target_mode '{target_mode}'")

    def spawn_projectile(self, projectile_id, spawn_position, impact_position, projectile_kwargs=None):
        projectile_cls = self.game_objects.registry.fetch('projectiles', projectile_id)
        if projectile_cls is None:
            raise RuntimeError(f"AreaSpawner '{self.spawn_id}' requested unknown projectile_id '{projectile_id}'")

        projectile_kwargs = projectile_kwargs or {}
        if projectile_kwargs:
            projectile = projectile_cls(spawn_position, self.game_objects, **projectile_kwargs)
        else:
            projectile = projectile_cls(spawn_position, self.game_objects)
        self.game_objects.projectiles.add_enemy(projectile)

    def spawn_warning_particles(self, spawn_position, impact_position, particle_type=None):
        camera_top = self.game_objects.camera_manager.camera.scroll[1]
        warning_y = max(spawn_position[1], camera_top - 18)
        resolved_particle_type = particle_type or self.warning_particle_type

        for _ in range(self.warning_particles):
            particle_position = [
                spawn_position[0] + random.randint(-self.warning_spread, self.warning_spread),
                warning_y - random.randint(0, 10),
            ]
            self.game_objects.particles.emit(
                resolved_particle_type,
                particle_position,
                n=1,
            )
