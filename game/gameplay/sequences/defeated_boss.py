import random

from engine import constants as C
from engine.system.sequence_manager import Sequence


class DefeatedBoss(Sequence):
    def __init__(self, game_objects, manager, key, boss):
        super().__init__(game_objects, manager, key)
        self.boss = boss
        self.time = 0
        self.timescale = 1
        self.number_particles = 0

        self.game_objects.signals.subscribe('boss_reward_collected', self.on_reward_collected)
        self.game_objects.signals.subscribe('particles_absorbed', self.on_particles_absorbed)

        self.game_objects.world_state.statistics_state.increase_progress()
        self.game_objects.world_state.narrative.mark_boss_defeated(str(type(boss).__name__).lower())
        self.game_objects.world_state.narrative.mark_flow_complete('boss_enconuter')

    def update(self, dt):
        if self.timescale == 0:
            return

        self.time += dt * self.timescale
        if self.time > 10:
            rect = self.boss.hitbox
            position = [
                rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5),
                rect.centery + random.uniform(rect[3] * 0.1, rect[3] * 0.5),
            ]
            self.game_objects.particles.emit("spirit_wisp", pos=position, n=1, colour=C.spirit_colour)
            self.time = 0

    def on_reward_collected(self, **kwargs):        
        self.number_particles = 10
        self.game_objects.particles.emit(
            "converging_soul",
            pos=kwargs.get('position', self.game_objects.player.hitbox.center),
            n=self.number_particles,
            player=self.game_objects.player,
        )
        self.timescale = 0

    def on_particles_absorbed(self):
        self.number_particles -= 1
        if self.number_particles <= 0:
            self.game_objects.game.state_manager.enter_state(state_name='instructions')
            self.finish()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('boss_reward_collected', self.on_reward_collected)
        self.game_objects.signals.unsubscribe('particles_absorbed', self.on_particles_absorbed)
