import random

from gameplay.data.boss_encounter_configs import get_boss_encounter_config
from gameplay.entities.visuals.cosmetics import ShockWave, SpiritFlash
from gameplay.entities.visuals.environments import GodRaysRadial
from gameplay.entities.visuals.environments.space_time_crack import SpaceTimeCrack
from gameplay.sequences.base import Sequence

from .boss_encounter_runtime import parse_pair, resolve_boss_for_encounter


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

        self.encounter_key = kwargs["encounter"]
        self.config = get_boss_encounter_config(self.encounter_key)
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
            signal_name = action.get('signal', self.entity.ID if self.entity is not None else self.encounter_key)
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
        elif action_type == 'spawn_god_rays':
            self._spawn_god_rays(action)
        elif action_type == 'spawn_flash':
            self._spawn_flash(action)
        elif action_type == 'spawn_shockwave':
            self._spawn_shockwave(action)
        elif action_type == 'emit_particles':
            self._emit_particles(action)
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
        elif action_type == 'reveal_boss':
            self._reveal_boss(action)
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
        self.entity = resolve_boss_for_encounter(self.game_objects, self.encounter_key, self.config, self.actors)
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

    def _spawn_god_rays(self, action):
        properties = dict(action.get('properties', {}))
        if 'state' in action:
            properties['state'] = action['state']
        if 'state_kwargs' in action:
            properties['state_kwargs'] = action['state_kwargs']
        rays = GodRaysRadial(
            self._resolve_action_position(action),
            self.game_objects,
            parallax=action.get('parallax', [1, 1]),
            size=tuple(action.get('size', [480, 480])),
            **properties,
        )
        return self._register_action_actor(action, rays)

    def _spawn_flash(self, action):
        flash = SpiritFlash(
            self._resolve_action_position(action),
            self.game_objects,
            **action.get('properties', {}),
        )
        return self._register_action_actor(action, flash)

    def _spawn_shockwave(self, action):
        wave = ShockWave(
            self._resolve_action_position(action),
            self.game_objects,
            **action.get('properties', {}),
        )
        return self._register_action_actor(action, wave)

    def _emit_particles(self, action):
        base_position = self._resolve_action_position(action)
        spread = parse_pair(action.get('spread', [0, 0]))
        count = int(action.get('count', 1))
        particle_count = int(action.get('particle_count', 1))
        particle_kwargs = dict(action.get('kwargs', {}))
        preset = action['preset']

        for _ in range(count):
            position = [
                base_position[0] + random.uniform(-spread[0], spread[0]),
                base_position[1] + random.uniform(-spread[1], spread[1]),
            ]
            self.game_objects.particles.emit(preset, position, n=particle_count, **particle_kwargs)

    def _reveal_boss(self, action):
        boss = self.entity or self._spawn_boss()
        previous_aggro = boss.flags.get('aggro', True)
        previous_attackable = boss.flags.get('attack_able', True)
        boss.flags['aggro'] = False
        boss.flags['attack_able'] = False
        boss.hit_component.set_invincibility(True)
        boss.velocity = [0, 0]

        duration = float(action.get('duration', 30))
        outline = boss.shader_state.effects.shaders.get('transparent_outline')
        if outline is not None:
            outline.reveal = 0.0
            outline.reveal_speed = action.get('outline_reveal_speed', 1.0 / max(duration, 1.0))

        def _finish_reveal():
            boss.flags['aggro'] = previous_aggro
            boss.flags['attack_able'] = previous_attackable
            boss.hit_component.set_invincibility(False)

        boss.shader_state.enter_state(
            'Materialize',
            duration=duration,
            colour=action.get('colour', [0.92, 0.97, 1.0, 1.0]),
            size=action.get('size', 0.12),
            on_complete=_finish_reveal,
        )

    def _register_action_actor(self, action, actor):
        group_name = action.get('group', 'cosmetics')
        getattr(self.game_objects, group_name).add(actor)
        actor_id = action.get('id')
        if actor_id is not None:
            self.actors[actor_id] = actor
            if not action.get('persist', False):
                self._temporary_actor_ids.add(actor_id)
        return actor

    def _resolve_action_position(self, action):
        if 'position' in action:
            return parse_pair(action['position'])

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

        offset = parse_pair(action.get('offset', [0, 0]))
        return [base[0] + offset[0], base[1] + offset[1]]

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
