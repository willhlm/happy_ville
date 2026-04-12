from engine.system.sequence_manager import Sequence
from gameplay.entities.visuals.cosmetics import SpawnEffect


class DeathSequence(Sequence):
    blocks_gameplay_input = True

    def __init__(self, game_objects, manager, key):
        super().__init__(game_objects, manager, key)
        self.stage = 0
        self.timer = 0
        self.game_objects.signals.subscribe('finish_spawn_effect', self.finish_spawn_effect)
        self.game_objects.game.state_manager.exit_to_state('gameplay')

    def update(self, dt):
        self.timer += dt
        if self.stage == 0 and self.timer > 120:
            self._begin_respawn_transition()
        elif self.stage == 1:
            self._spawn_effect()

    def finish_spawn_effect(self):
        self.game_objects.player.currentstate.enter_state('respawn')
        self.finish()

    def _begin_respawn_transition(self):
        map_name, point = self._get_spawn_point()
        active_state = self.game_objects.game.state_manager.state_stack[-1]
        self.game_objects.transition.run(
            previous_state=active_state,
            style="fade_black",
            action=lambda: self.game_objects.map.load_now(map_name, point),
            on_covered=self._on_respawn_map_ready,
            after=self._on_respawn_map_loaded,
        )
        self.stage = 99

    def _get_spawn_point(self):
        spawn_point = self.game_objects.player.backpack.map.spawn_point
        if spawn_point.get('bone', False):
            map_name = spawn_point['bone']['map']
            point = spawn_point['bone']['point']
            del spawn_point['bone']
            return map_name, point

        return spawn_point['map'], spawn_point['point']

    def _on_respawn_map_ready(self):
        self.game_objects.player.currentstate.enter_state("invisible")

    def _on_respawn_map_loaded(self):
        self.stage = 1

    def _spawn_effect(self):
        spawneffect = SpawnEffect((0, 0), self.game_objects)
        spawneffect.rect.midbottom = self.game_objects.player.rect.midbottom
        spawneffect.rect.bottom += 100
        self.game_objects.cosmetics.add(spawneffect)
        self.stage = 2

    def cleanup(self):
        self.game_objects.signals.unsubscribe('finish_spawn_effect', self.finish_spawn_effect)
