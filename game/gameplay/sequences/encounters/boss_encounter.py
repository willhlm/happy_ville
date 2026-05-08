from gameplay.data.boss_encounter_configs import get_boss_encounter_config
from gameplay.sequences.base import Sequence


class BossEncounter(Sequence):
    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    def __init__(self, game_objects, manager, key, **kwargs):
        super().__init__(game_objects, manager, key)
        self.timer = 0
        self.pos = [-self.game_objects.game.window_size[1], self.game_objects.game.window_size[1]]
        self.const = [0.8, 0.8]
        self.rect1 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect2 = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.rect1.clear(0, 0, 0, 255)
        self.rect2.clear(0, 0, 0, 255)

        self.game_objects.game.state_manager.exit_to_state('gameplay')

        self.entity = kwargs.get('entity')
        if not self.entity and kwargs.get('ID'):
            self.entity = game_objects.map.ctx.references[kwargs['ID']]

        self.encounter_id = kwargs['ID']
        self.config = get_boss_encounter_config(self.encounter_id)
        self.steps = self.config.get('steps', [])
        self.step_index = 0

        camera = self.config.get('camera')
        if camera:
            self.game_objects.camera_manager.set_camera(camera)

        for action in self.config.get('setup_actions', []):
            self._run_action(action)

    def update(self, dt):
        self.timer += dt

        while self.step_index < len(self.steps) and self.timer > self.steps[self.step_index]['time']:
            for action in self.steps[self.step_index].get('actions', []):
                self._run_action(action)
            self.step_index += 1

    def update_render(self, dt):
        self.pos[0] += dt
        self.pos[1] -= dt
        self.pos[0] = min(-self.game_objects.game.window_size[1] * self.const[0], self.pos[0])
        self.pos[1] = max(self.game_objects.game.window_size[1] * self.const[1], self.pos[1])

    def render(self, target):
        self.game_objects.game.display.render(self.rect1.texture, target, position=[0, self.pos[0]])
        self.game_objects.game.display.render(self.rect2.texture, target, position=[0, self.pos[1]])

    def _run_action(self, action):
        action_type = action['type']
        player = self.game_objects.player

        if action_type == 'player_shader_input':
            player.shader_state.handle_input(action['input'])
        elif action_type == 'player_state':
            player.currentstate.enter_state(action['state'])
        elif action_type == 'player_acceleration_x':
            player.acceleration[0] = action['value']
        elif action_type == 'player_velocity_x':
            player.velocity[0] = action['value']
        elif action_type == 'boss_tasks':
            self.entity.currentstate.clear_tasks()
            for task in action.get('tasks', []):
                self.entity.currentstate.queue_task(**task)
            if action.get('start', True):
                self.entity.currentstate.start_next_task()
        elif action_type == 'boss_start_aggro':
            self.entity.start_aggro(delay=action.get('delay', 0))
        elif action_type == 'camera_exit':
            self.game_objects.camera_manager.camera.exit_state()
        elif action_type == 'mark_flow_complete':
            if self.entity.ID:
                self.game_objects.world_state.narrative.mark_flow_complete(self.entity.ID)
        elif action_type == 'exit_state':
            self.finish()

    def cleanup(self):
        self.rect1.release()
        self.rect2.release()
