from .sprite_groups import Group, CombinedGroup


class ProjectileRouter:
    def __init__(self, add_callback):
        self._add_callback = add_callback

    def add(self, *projectiles):
        for projectile in projectiles:
            self._add_callback(projectile)


class ProjectileGroups:
    def __init__(self):
        self.enemy = Group()
        self.friendly = Group()
        self.enemy_platform = Group()
        self.friendly_platform = Group()
        self._all_friendly = CombinedGroup(self.friendly, self.friendly_platform)
        self._all_enemy = CombinedGroup(self.enemy, self.enemy_platform)
        self._all = CombinedGroup(self.friendly, self.friendly_platform, self.enemy, self.enemy_platform)
        self.enemy_router = ProjectileRouter(self.add_enemy)
        self.friendly_router = ProjectileRouter(self.add_friendly)

    def add_friendly(self, projectile):
        if getattr(projectile, 'uses_platform_physics', False):
            self.friendly_platform.add(projectile)
        else:
            self.friendly.add(projectile)

    def add_enemy(self, projectile):
        if getattr(projectile, 'uses_platform_physics', False):
            self.enemy_platform.add(projectile)
        else:
            self.enemy.add(projectile)

    def all_friendly(self):
        return self._all_friendly

    def all_enemy(self):
        return self._all_enemy

    def all(self):
        return self._all

    def update(self, dt):
        self.friendly.update(dt)
        self.friendly_platform.update(dt)
        self.enemy.update(dt)
        self.enemy_platform.update(dt)

    def update_render(self, dt):
        self.friendly.update_render(dt)
        self.friendly_platform.update_render(dt)
        self.enemy.update_render(dt)
        self.enemy_platform.update_render(dt)

    def draw(self, target):
        self.friendly.draw(target)
        self.friendly_platform.draw(target)
        self.enemy.draw(target)
        self.enemy_platform.draw(target)

    def empty(self):
        self.enemy.empty()
        self.friendly.empty()
        self.enemy_platform.empty()
        self.friendly_platform.empty()
