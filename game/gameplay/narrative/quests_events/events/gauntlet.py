import random

from gameplay.data.gauntlet_configs import get_gauntlet_config
from gameplay.narrative.quests_events.base import Tasks


class Gauntlet(Tasks):
    FINAL_KILL_FREEZE_DURATION = 50
    FINAL_KILL_SLOW_DURATION = 100
    FINAL_KILL_SLOW_SCALE = 0.5

    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.gauntlet_id = kwarg.get("ID", game_objects.map.biome_room_name)
        self.config = get_gauntlet_config(self.gauntlet_id)
        self.wave_index = -1
        self.gate_ids = self.config.get("gates", [])
        self.active_signal_counts = {}
        self.signal_callbacks = {}
        self.completed = False
        self.cleaned_up = False
        self.timer_id = f"gauntlet_{self.gauntlet_id}"
        self.delay_between_waves = self.config.get("delay_between_waves", 0)
        self.spawn_wait_time = self.config.get("spawn_wait_time", 100)
        self.spawn_warning_duration = self.config.get("spawn_warning_duration", 0)
        self.spawn_effect_config = self.config.get("spawn_effect", False)
        self.spawn_warning_effect_config = self.config.get("spawn_warning_effect", False)
        self.spawn_warning_interval = self.config.get("spawn_warning_interval", 8)

        self.game_objects.signals.subscribe("player_died", self.handle_player_death)

        self.close_gates()
        self._schedule_start()

    def close_gates(self):
        for gate_id in self.gate_ids:
            self.game_objects.signals.emit(gate_id, action="close")

    def open_gates(self):
        for gate_id in self.gate_ids:
            self.game_objects.signals.emit(gate_id, action="open")

    def _schedule_start(self):
        delay = self.config.get("delay_before_start", 0)
        self._schedule_timer(delay, self.start_next_wave)

    def _schedule_timer(self, duration, callback):
        self.game_objects.timer_manager.start_timer(max(0, duration), callback, ID=self.timer_id)

    def start_next_wave(self):
        self.wave_index += 1
        waves = self.config.get("waves", [])
        if self.wave_index >= len(waves):
            self.complete()
            return

        wave = waves[self.wave_index]
        self.begin_wave(wave)

    def begin_wave(self, wave):
        warning_duration = wave.get("spawn_warning_duration", self.spawn_warning_duration)
        self._spawn_wave_warning(wave, warning_duration)
        if warning_duration > 0:
            self._schedule_timer(warning_duration, lambda wave=wave: self._activate_wave(wave))
        else:
            self._activate_wave(wave)

    def _activate_wave(self, wave):
        self.spawn_wave(wave)
        self.set_wave_signal_counts(wave)

        if not self.active_signal_counts:
            self.start_next_wave()

    def spawn_wave(self, wave):
        spawn_wait_time = wave.get("spawn_wait_time", self.spawn_wait_time)
        for enemy_data in wave.get("spawns", []):
            enemy_name = enemy_data["enemy"]
            enemy_cls = self.game_objects.registry.fetch("enemies", enemy_name)
            if enemy_cls is None:
                raise KeyError(f"Unknown gauntlet enemy '{enemy_name}' in '{self.gauntlet_id}'.")

            spawn_pos = list(enemy_data["pos"])
            self._spawn_effect(spawn_pos)
            enemy_kwargs = dict(enemy_data.get("kwargs", {}))
            enemy = enemy_cls(spawn_pos, self.game_objects, **enemy_kwargs)
            self.game_objects.enemies.add(enemy)
            self._apply_spawn_wait(enemy, enemy_data.get("spawn_wait_time", spawn_wait_time))

    def set_wave_signal_counts(self, wave):
        self._unsubscribe_wave_signals()
        self.active_signal_counts = {}

        for signal_name, count in self._collect_signal_counts(wave).items():
            if count <= 0:
                continue
            self.active_signal_counts[signal_name] = count
            callback = self._make_signal_callback(signal_name)
            self.signal_callbacks[signal_name] = callback
            self.game_objects.signals.subscribe(signal_name, callback)

    def _collect_signal_counts(self, wave):
        signal_counts = {}
        for enemy_data in wave.get("spawns", []):
            signal_name = enemy_data.get("kill_signal") or self._default_kill_signal(enemy_data["enemy"])
            if not signal_name:
                raise ValueError(
                    f"Gauntlet '{self.gauntlet_id}' is missing a kill signal for enemy '{enemy_data['enemy']}'."
                )
            signal_counts[signal_name] = signal_counts.get(signal_name, 0) + 1
        return signal_counts

    def _default_kill_signal(self, enemy_name):
        return self.config.get("kill_signals", {}).get(enemy_name)

    def _make_signal_callback(self, signal_name):
        def _callback(**_kwargs):
            remaining = self.active_signal_counts.get(signal_name, 0)
            if remaining <= 0:
                return

            self.active_signal_counts[signal_name] = remaining - 1
            if self.active_signal_counts[signal_name] <= 0:
                del self.active_signal_counts[signal_name]
            if not self.active_signal_counts:
                if self._is_last_wave():
                    self._play_final_kill_time_effect()
                    self.complete()
                else:
                    self._schedule_timer(self.delay_between_waves, self.start_next_wave)

        return _callback

    def _is_last_wave(self):
        return self.wave_index >= len(self.config.get("waves", [])) - 1

    def _play_final_kill_time_effect(self):
        self.game_objects.time_manager.modify_time(
            time_scale=self.FINAL_KILL_SLOW_SCALE,
            duration=self.FINAL_KILL_SLOW_DURATION,
        )
        self.game_objects.time_manager.modify_time(
            time_scale=0,
            duration=self.FINAL_KILL_FREEZE_DURATION,
        )

    def _spawn_wave_warning(self, wave, warning_duration):
        if not self.spawn_warning_effect_config:
            return

        interval = wave.get("spawn_warning_interval", self.spawn_warning_interval)
        for enemy_data in wave.get("spawns", []):
            self._spawn_warning_at(enemy_data["pos"], warning_duration, interval)

    def _spawn_warning_at(self, spawn_pos, warning_duration, interval):
        self._spawn_configured_effect(spawn_pos, self.spawn_warning_effect_config)
        if interval <= 0 or warning_duration <= interval:
            return

        self._schedule_timer(
            interval,
            lambda spawn_pos=spawn_pos, warning_duration=warning_duration - interval, interval=interval:
                self._spawn_warning_at(spawn_pos, warning_duration, interval),
        )

    def _spawn_effect(self, spawn_pos):
        if not self.spawn_effect_config:
            return

        self._spawn_configured_effect(spawn_pos, self.spawn_effect_config)

    def _spawn_configured_effect(self, spawn_pos, effect_config):
        if not effect_config:
            return

        if isinstance(effect_config, dict):
            effect_name = effect_config.get("name", "enemy_spawn_effect")
            offset = effect_config.get("offset", [0, 0])
            position_jitter = effect_config.get("position_jitter", [0, 0])
            effect_kwargs = {
                key: value
                for key, value in effect_config.items()
                if key not in {"name", "offset", "position_jitter"}
            }
        else:
            effect_name = effect_config
            offset = [0, 0]
            position_jitter = [0, 0]
            effect_kwargs = {}

        effect_cls = self._resolve_spawn_effect_class(effect_name)
        effect_pos = self._randomize_effect_position(spawn_pos, offset, position_jitter)
        self.game_objects.cosmetics.add(effect_cls(effect_pos, self.game_objects, **effect_kwargs))

    def _randomize_effect_position(self, spawn_pos, offset, position_jitter):
        jitter_x = random.uniform(-position_jitter[0], position_jitter[0])
        jitter_y = random.uniform(-position_jitter[1], position_jitter[1])
        return [
            spawn_pos[0] + offset[0] + jitter_x,
            spawn_pos[1] + offset[1] + jitter_y,
        ]

    def _apply_spawn_wait(self, enemy, wait_time):
        if wait_time <= 0:
            return

        enemy.currentstate.enter_state(
            "wait",
            time=wait_time,
            next_state=enemy.config.get("initial_state", "patrol"),
        )

    def _resolve_spawn_effect_class(self, effect_name):
        if not isinstance(effect_name, str) or not effect_name:
            raise ValueError(f"Invalid spawn effect name '{effect_name}' in '{self.gauntlet_id}'.")

        effect_cls = self.game_objects.registry.fetch("cosmetics", effect_name)
        if effect_cls is None:
            raise KeyError(f"Unknown gauntlet spawn effect '{effect_name}' in '{self.gauntlet_id}'.")
        return effect_cls

    def _spawn_completion_reward(self):
        reward_config = self.config.get("on_complete_reward")
        if not reward_config:
            return

        if isinstance(reward_config, str):
            item_name = reward_config
            position = list(self.game_objects.player.hitbox.center)
        else:
            item_name = reward_config["item"]
            position = list(reward_config.get("pos", self.game_objects.player.hitbox.center))

        reward_cls = self.game_objects.registry.fetch("items", item_name)
        if reward_cls is None:
            raise KeyError(f"Unknown gauntlet reward '{item_name}' in '{self.gauntlet_id}'.")

        self.game_objects.loot.add(reward_cls(position, self.game_objects))

    def complete(self):
        if self.completed:
            return
        self.completed = True
        self.game_objects.world_state.narrative.mark_flow_complete(self.gauntlet_id)
        self.game_objects.world_state.narrative.update_event(self.gauntlet_id)
        self._spawn_completion_reward()
        self.open_gates()
        self.cleanup()

    def handle_player_death(self):
        self.open_gates()
        self.cleanup()

    def cleanup(self):
        if self.cleaned_up:
            return
        self.cleaned_up = True
        self.game_objects.timer_manager.remove_ID_timer(self.timer_id)
        self._unsubscribe_wave_signals()
        self.game_objects.signals.unsubscribe("player_died", self.handle_player_death)

    def _unsubscribe_wave_signals(self):
        for signal_name, callback in self.signal_callbacks.items():
            self.game_objects.signals.unsubscribe(signal_name, callback)
        self.signal_callbacks = {}
