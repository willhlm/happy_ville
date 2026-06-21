from .spawners import FallbackProjectileSpawner


class AreaManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._spawners_by_id = {}
        self._fallback_spawners = []

    def clear(self):
        for spawners in list(self._spawners_by_id.values()):
            for spawner in list(spawners):
                spawner.kill()
        for spawner in list(self._fallback_spawners):
            spawner.kill()
        self._spawners_by_id.clear()
        self._fallback_spawners.clear()

    def register_spawner(self, spawner):
        self._spawners_by_id.setdefault(spawner.spawn_id, []).append(spawner)

    def unregister_spawner(self, spawner):
        spawners = self._spawners_by_id.get(spawner.spawn_id)
        if not spawners:
            return
        if spawner in spawners:
            spawners.remove(spawner)
        if not spawners:
            self._spawners_by_id.pop(spawner.spawn_id, None)

    def get_spawners(self, spawn_id):
        return list(self._spawners_by_id.get(spawn_id, ()))

    def register_fallback_spawner(self, spawner):
        self._fallback_spawners.append(spawner)

    def unregister_fallback_spawner(self, spawner):
        if spawner in self._fallback_spawners:
            self._fallback_spawners.remove(spawner)

    def update(self, dt):
        for spawners in list(self._spawners_by_id.values()):
            for spawner in list(spawners):
                spawner.update(dt)
        for spawner in list(self._fallback_spawners):
            spawner.update(dt)

    def request_projectile_spawns(
        self,
        spawn_id,
        count=None,
        selector='all',
        fallback_projectile_id=None,
        projectile_kwargs=None,
        warning_callback=None,
        warning_delay=None,
        warning_interval=None,
        spawn_interval=None,
        spawn_origin='area',
        target_mode='random',
        target_offset=0,
        warning_particle_type=None,
    ):
        spawners = self.get_spawners(spawn_id)
        if not spawners:
            self._spawn_fallback_projectiles(
                spawn_id=spawn_id,
                count=count,
                fallback_projectile_id=fallback_projectile_id,
                projectile_kwargs=projectile_kwargs,
                warning_delay=warning_delay,
                warning_interval=warning_interval,
                spawn_interval=spawn_interval,
                warning_particle_type=warning_particle_type,
            )
            return

        if selector == 'nearest_to_player':
            player_x = self.game_objects.player.hitbox.centerx
            spawners = [min(spawners, key=lambda spawner: abs(spawner.hitbox.centerx - player_x))]
        elif selector != 'all':
            raise ValueError(f"Unknown AreaSpawner selector '{selector}'")

        for spawner in spawners:
            spawner.request_projectile_spawns(
                count=count,
                projectile_kwargs=projectile_kwargs,
                warning_callback=warning_callback,
                warning_delay=warning_delay,
                warning_interval=warning_interval,
                spawn_interval=spawn_interval,
                spawn_origin=spawn_origin,
                target_mode=target_mode,
                target_offset=target_offset,
                warning_particle_type=warning_particle_type,
            )

    def _spawn_fallback_projectiles(
        self,
        spawn_id,
        count,
        fallback_projectile_id,
        projectile_kwargs,
        warning_delay,
        warning_interval,
        spawn_interval,
        warning_particle_type,
    ):
        if fallback_projectile_id is None:
            raise RuntimeError(
                f"Projectile spawn requested for id='{spawn_id}' but no AreaSpawner zones were found and no fallback_projectile_id was provided"
            )

        projectile_count = 1 if count is None else int(count)
        fallback_spawner = FallbackProjectileSpawner(
            [0, 0],
            self.game_objects,
            projectile_id=fallback_projectile_id,
            projectile_count=projectile_count,
            projectile_kwargs=projectile_kwargs,
            warning_delay=40 if warning_delay is None else int(warning_delay),
            warning_interval=6 if warning_interval is None else int(warning_interval),
            spawn_interval=40 if spawn_interval is None else int(spawn_interval),
            warning_particle_type=warning_particle_type,
        )
