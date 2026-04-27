from .crawl import Crawl


class Chase(Crawl):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key, **kwargs)
        self.turn_delay = 0

    def update_logic(self, dt):
        super().update_logic(dt)

        self.turn_delay = max(0, self.turn_delay - dt)
        if abs(self.player_distance[0]) > self.entity.config['distances']['aggro'][0] or abs(self.player_distance[1]) > self.entity.config['distances']['aggro'][1]:
            return

        if self.turn_delay <= 0:
            self.entity.surface_stick_physics.set_direction_towards(self.entity.game_objects.player.hitbox.center)
            self.turn_delay = 15

        if abs(self.player_distance[0]) <= self.entity.config['distances']['attack'][0] and abs(self.player_distance[1]) <= self.entity.config['distances']['attack'][1]:
            if self.entity.currentstate.cooldowns.get('surface_attack') <= 0:
                self.enter_state('attack_pre')
