from gameplay.data.boss_encounter_configs import get_boss_encounter_config
from .base.cutscene_engine import CutsceneEngine

class BossEncounter(CutsceneEngine):
    def __init__(self, game, **kwarg):
        super().__init__(game)
        self.entity = kwarg.get('entity')
        if not self.entity and kwarg.get('ID'):
            self.entity = game.game_objects.map.ctx.references[kwarg['ID']]

        self.encounter_id = kwarg['ID']

        self.config = get_boss_encounter_config(self.encounter_id)
        self.steps = self.config.get('steps', [])
        self.step_index = 0

        camera = self.config.get('camera')
        if camera:
            self.game.game_objects.camera_manager.set_camera(camera)

        for action in self.config.get('setup_actions', []):
            self._run_action(action)

    def update(self, dt):
        super().update(dt)
        self.timer += dt

        while self.step_index < len(self.steps) and self.timer > self.steps[self.step_index]['time']:
            for action in self.steps[self.step_index].get('actions', []):
                self._run_action(action)
            self.step_index += 1

    def _run_action(self, action):
        action_type = action['type']
        player = self.game.game_objects.player

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
            self.entity.start_aggro(delay = action.get('delay', 0))
        elif action_type == 'camera_exit':
            self.game.game_objects.camera_manager.camera.exit_state()
        elif action_type == 'mark_cutscene_complete':
            if self.entity.ID:
                self.game.game_objects.world_state.narrative.mark_cutscene_complete(self.entity.ID)
        elif action_type == 'exit_state':
            self.game.state_manager.exit_state()
