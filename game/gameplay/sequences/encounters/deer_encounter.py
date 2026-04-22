from engine.system.sequence_manager import Sequence


class DeerEncounter(Sequence):
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

        pos = [2992, 848]
        self.entity = game_objects.registry.fetch('enemies', 'reindeer')(pos, game_objects)
        game_objects.enemies.add(self.entity)
        game_objects.camera_manager.set_camera('Deer_encounter')
        game_objects.player.currentstate.enter_state('Run_pre')

    def update(self, dt):
        self.timer += dt
        if self.stage == 0:
            if self.timer < 50:
                self.game_objects.player.velocity[0] = 4
            elif self.timer > 50:
                self.game_objects.player.currentstate.enter_state('Idle_main')
                self.game_objects.player.acceleration[0] = 0
                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:
                self.entity.currentstate.queue_task(task='walk', animation='walk_nice')
                self.entity.currentstate.queue_task(task='idle')
                self.entity.currentstate.start_next_task()

                self.entity.velocity[0] = 5
                self.entity.dir[0] *= -1
                self.stage = 2

        elif self.stage == 2:
            if self.timer > 200:
                self.entity.velocity[0] = 5

        if self.timer > 300:
            self.finish()

    def update_render(self, dt):
        self.pos[0] += dt
        self.pos[1] -= dt
        self.pos[0] = min(-self.game_objects.game.window_size[1] * self.const[0], self.pos[0])
        self.pos[1] = max(self.game_objects.game.window_size[1] * self.const[1], self.pos[1])

    def render(self, target):
        self.game_objects.game.display.render(self.rect1.texture, target, position=[0, self.pos[0]])
        self.game_objects.game.display.render(self.rect2.texture, target, position=[0, self.pos[1]])

    def cleanup(self):
        self.game_objects.camera_manager.camera.exit_state()
        self.entity.kill()
        self.game_objects.world_state.narrative.mark_flow_complete('deer_encounter')
        self.rect1.release()
        self.rect2.release()
