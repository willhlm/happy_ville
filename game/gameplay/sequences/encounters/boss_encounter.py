from gameplay.data.boss_encounter_configs import get_boss_encounter_config
from gameplay.entities.visuals.environments.space_time_crack import SpaceTimeCrack
from gameplay.sequences.base import Sequence

from .boss_encounter_runtime import resolve_boss_for_encounter


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
        self.actors = {}
        self._temporary_actor_ids = set()

        self.game_objects.game.state_manager.exit_to_state('gameplay')

        self.encounter_id = kwargs['ID']
        self.config = get_boss_encounter_config(self.encounter_id)
        self.entity = None
        source = kwargs.get('source')
        if source is not None:
            self.actors['source'] = source
        if self._should_resolve_boss_on_start():
            self._spawn_boss()
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
        elif action_type == 'emit_signal':
            signal_name = action.get('signal', self.entity.ID if self.entity is not None else self.encounter_id)
            if signal_name:
                self.game_objects.signals.emit(signal_name, **action.get('kwargs', {}))
        elif action_type == 'boss_state':
            if self.entity is None:
                self._spawn_boss()
            self.entity.currentstate.enter_state(action['state'], **action.get('kwargs', {}))
        elif action_type == 'boss_method':
            if self.entity is None:
                self._spawn_boss()
            getattr(self.entity, action['method'])(**action.get('kwargs', {}))
        elif action_type == 'spawn_boss':
            self._spawn_boss()
        elif action_type == 'spawn_crack':
            self._spawn_crack(action)
        elif action_type == 'actor_method':
            actor = self.actors[action['actor']]
            getattr(actor, action['method'])(**action.get('kwargs', {}))
        elif action_type == 'actor_state':
            actor = self.actors[action['actor']]
            actor.enter_state(action['state'], **action.get('kwargs', {}))
        elif action_type == 'kill_actor':
            self._kill_actor(action['actor'])
        elif action_type == 'camera_exit':
            self.game_objects.camera_manager.camera.exit_state()
        elif action_type == 'mark_flow_complete':
            if self.entity is not None and self.entity.ID:
                self.game_objects.world_state.narrative.mark_flow_complete(self.entity.ID)
        elif action_type == 'exit_state':
            self.finish()

    def _should_resolve_boss_on_start(self):
        boss_config = self.config.get('boss')
        if boss_config is None:
            return False
        return boss_config.get('spawn_timing', 'start') != 'action'

    def _spawn_boss(self):
        if self.entity is not None:
            return self.entity
        self.entity = resolve_boss_for_encounter(self.game_objects, self.encounter_id, self.config, self.actors)
        self.actors['boss'] = self.entity
        return self.entity

    def _spawn_crack(self, action):
        properties = dict(action.get('properties', {}))
        if 'state' in action:
            properties['state'] = action['state']
        if 'state_kwargs' in action:
            properties['state_kwargs'] = action['state_kwargs']
        crack = SpaceTimeCrack(
            self._resolve_action_position(action),
            self.game_objects,
            tuple(action.get('size', [300, 300])),
            parallax=action.get('parallax', [1, 1]),
            layer_name=action.get('layer_name', 'player'),
            **properties,
        )
        group_name = action.get('group', 'cosmetics_bg')
        getattr(self.game_objects, group_name).add(crack)
        actor_id = action.get('id', 'crack')
        self.actors[actor_id] = crack
        if not action.get('persist', False):
            self._temporary_actor_ids.add(actor_id)
        return crack

    def _resolve_action_position(self, action):
        if 'position' in action:
            parts = [part.strip() for part in action['position'].split(',')]
            return [int(float(parts[0])), int(float(parts[1]))]

        relative_to = action.get('relative_to')
        actor = self.actors[relative_to]
        anchor = action.get('anchor', 'center')
        rect = getattr(actor, 'hitbox', None) or getattr(actor, 'rect', None)
        if anchor == 'topleft':
            base = [rect.left, rect.top]
        elif anchor == 'midbottom':
            base = [rect.midbottom[0], rect.midbottom[1]]
        else:
            base = [rect.centerx, rect.centery]

        offset = action.get('offset', '0,0').split(',')
        return [base[0] + int(float(offset[0])), base[1] + int(float(offset[1]))]

    def _kill_actor(self, actor_id):
        actor = self.actors.pop(actor_id, None)
        if actor is None:
            return
        self._temporary_actor_ids.discard(actor_id)
        if actor is not self.entity:
            actor.kill()

    def cleanup(self):
        for actor_id in list(self._temporary_actor_ids):
            self._kill_actor(actor_id)
        self.rect1.release()
        self.rect2.release()
