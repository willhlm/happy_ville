import random
from .pending_spawn import PendingSpawn

class FallbackProjectileSpawner:
    def __init__(
        self,
        pos,
        game_objects,
        projectile_id,
        projectile_count,
        projectile_kwargs=None,
        warning_delay=40,
        warning_interval=6,
        spawn_interval=40,
        warning_particle_type=None,
    ):
        self.game_objects = game_objects
        self.pos = pos
        self.projectile_id = projectile_id
        self.projectile_kwargs = projectile_kwargs or {}
        self.pending_spawns = []
        self.game_objects.areas.register_fallback_spawner(self)

        for projectile_index in range(projectile_count):
            spawn_position, impact_position = self._sample_spawn_positions()
            timer = warning_delay + projectile_index * spawn_interval
            self.pending_spawns.append(
                PendingSpawn(
                    spawn_position=spawn_position,
                    impact_position=impact_position,
                    timer=timer,
                    warning_window=warning_delay,
                    warning_interval=warning_interval,
                    warning_callback=self._build_warning_callback(warning_particle_type),
                    spawn_callback=self._spawn_projectile,
                )
            )

    def kill(self):
        self.game_objects.areas.unregister_fallback_spawner(self)

    def update(self, dt):
        completed_spawns = []
        for pending_spawn in self.pending_spawns:
            pending_spawn.update(dt)

            if pending_spawn.should_warn():
                pending_spawn.warning_callback(pending_spawn.spawn_position, pending_spawn.impact_position)
                pending_spawn.reset_warning_timer()

            if pending_spawn.should_spawn():
                pending_spawn.spawn_callback(pending_spawn.spawn_position)
                completed_spawns.append(pending_spawn)

        for pending_spawn in completed_spawns:
            self.pending_spawns.remove(pending_spawn)

        if not self.pending_spawns:
            self.kill()

    def _sample_spawn_positions(self):
        camera = self.game_objects.camera_manager.camera
        camera_left = int(camera.scroll[0])
        camera_top = int(camera.scroll[1])
        camera_width = self.game_objects.game.window_size[0]
        camera_height = self.game_objects.game.window_size[1]
        spawn_x = random.randint(camera_left, camera_left + max(0, camera_width - 1))
        spawn_y = camera_top - 24
        spawn_position = [spawn_x, spawn_y]
        impact_position = [spawn_x, spawn_y + camera_height]
        return spawn_position, impact_position

    def _build_warning_callback(self, particle_type):
        if particle_type is None:
            return None
        return lambda spawn_position, impact_position: self.game_objects.particles.emit(
            particle_type,
            [spawn_position[0], spawn_position[1] + 6],
            n=1,
        )

    def _spawn_projectile(self, spawn_position):
        projectile_cls = self.game_objects.registry.fetch('projectiles', self.projectile_id)
        if projectile_cls is None:
            raise RuntimeError(f"AreaManager fallback requested unknown projectile_id '{self.projectile_id}'")

        if self.projectile_kwargs:
            projectile = projectile_cls(spawn_position, self.game_objects, **self.projectile_kwargs)
        else:
            projectile = projectile_cls(spawn_position, self.game_objects)
        self.game_objects.projectiles.add_enemy(projectile)
