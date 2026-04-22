from engine.system.sequence_manager import Sequence


class ButterflyEncounter(Sequence):
    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    def __init__(self, game_objects, manager, key, **kwargs):
        super().__init__(game_objects, manager, key)
        self.stage = 0
        self.timer = 0
        self.entity = None
        self.pos = [-self.game_objects.game.window_size[1], self.game_objects.game.window_size[1]]
        self.const = [0.8, 0.9]
        self.rect1 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect2 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect1.clear(0, 0, 0, 255)
        self.rect2.clear(0, 0, 0, 255)

        self.game_objects.game.state_manager.exit_to_state('gameplay')
        self.game_objects.signals.emit('who_is_cocoon', callback=self.set_entity)

    def set_entity(self, entity):
        self.entity = entity

    def update(self, dt):
        self.timer += dt
        if self.stage == 0:
            if self.timer < 50:
                self.game_objects.player.velocity[0] = 4
                self.game_objects.player.acceleration[0] = 1
            elif self.timer > 150:
                self.game_objects.player.currentstate.enter_state('Idle_main')
                self.game_objects.player.acceleration[0] = 0
                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:
                self.game_objects.camera_manager.camera_shake(duration=200)
                self.stage = 2

        elif self.stage == 2:
            if self.entity:
                self.entity.particle_release()
            if self.timer > 400:
                self.game_objects.quests_events.initiate_event('butterfly_encounter')
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
        self.rect1.release()
        self.rect2.release()
