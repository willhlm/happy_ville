from gameplay.entities.projectiles.base.melee import Melee

class Counter(Melee):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = self.entity.hitbox.copy()
        self.dmg = 0
        self.entity.flags['invincibility'] = True#make the player invincible

    def update(self, dt):
        self.lifetime -= dt
        self.destroy()

    def collision_enemy(self, collision_enemy):
        self.counter()

    def collision_projectile(self, eprojectile):
        self.counter()

    def counter(self):
        if self.flags['invincibility']: return#such that it only collides ones
        self.flags['invincibility'] = True
        self.entity.game_objects.timer_manager.start_timer(C.invincibility_time_player, self.entity.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.entity.abilities.spirit_abilities['Slow_motion'].counter()#slow motion

    def kill(self):
        super().kill()
        self.entity.abilities.spirit_abilities['Slow_motion'].exit()

    def draw(self, target):
        pass
