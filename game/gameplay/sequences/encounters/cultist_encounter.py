from gameplay.sequences.base import Sequence


class CultistEncounter(Sequence):
    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    def __init__(self, game_objects, manager, key, **kwargs):
        super().__init__(game_objects, manager, key)
        self.timer = 0
        self.stage = 0
        self.pos = [-self.game_objects.game.window_size[1], self.game_objects.game.window_size[1]]
        self.const = [0.8, 0.8]
        self.rect1 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect2 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect1.clear(0, 0, 0, 255)
        self.rect2.clear(0, 0, 0, 255)

        self.game_objects.game.state_manager.exit_to_state('gameplay')
        self.game_objects.player.death_manager.set_override(self.handle_player_death)
        self.game_objects.quests_events.initiate_event('cultist_encounter', kill=2)
        self.game_objects.camera_manager.set_camera('Cultist_encounter')
        self.game_objects.player.currentstate.enter_state('run')

    def update(self, dt):
        self.timer += dt
        if self.stage == 0:
            if self.timer < 50:
                self.game_objects.player.velocity[0] = -4
                self.game_objects.player.acceleration[0] = 1
            elif self.timer > 50:
                self.game_objects.player.currentstate.enter_state('idle')
                self.game_objects.player.acceleration[0] = 0
                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:
                spawn_pos = self.game_objects.player.rect.topright
                entity2 = self.game_objects.registry.fetch('enemies', 'cultist_rogue')(spawn_pos, self.game_objects)
                entity2.dir[0] = -1
                entity2.currentstate.enter_state('Ambush_pre')
                self.game_objects.enemies.add(entity2)

                self.stage = 2
                self.timer = 0

        elif self.stage == 2:
            if self.timer > 100:
                self.finish()

    def update_render(self, dt):
        self.pos[0] += dt
        self.pos[1] -= dt
        self.pos[0] = min(-self.game_objects.game.window_size[1] * self.const[0], self.pos[0])
        self.pos[1] = max(self.game_objects.game.window_size[1] * self.const[1], self.pos[1])

    def render(self, target):
        self.game_objects.game.display.render(self.rect1.texture, target, position=[0, self.pos[0]])
        self.game_objects.game.display.render(self.rect2.texture, target, position=[0, self.pos[1]])

    def handle_player_death(self):
        player = self.game_objects.player
        player.reset_movement()
        active_state = self.game_objects.game.state_manager.state_stack[-1]
        self.game_objects.map.load_map(active_state, 'dark_forest_1', '1')
        player.death_manager.clear_override()
        self.finish()

    def cleanup(self):
        self.game_objects.player.death_manager.clear_override()
        self.game_objects.camera_manager.camera.exit_state()
        self.rect1.release()
        self.rect2.release()
