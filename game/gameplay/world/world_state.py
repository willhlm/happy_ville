from engine.utils import read_files

class WorldObjectState:
    DEFAULT_LEVEL_STATE = {
        'loot_container': {},
        'lever': {},
        'gate': {},
        'soul_essence': {},
        'runestone': {},
        'interactable_items': {},
        'breakable_platform': {},
        'bg_fade': {},
    }

    def __init__(self, state):
        self.state = state

    def init_level(self, level_name):
        self.state[level_name] = {
            bucket: values.copy()
            for bucket, values in self.DEFAULT_LEVEL_STATE.items()
        }

    def _bucket(self, level_name: str, bucket: str) -> dict:
        self.state[level_name].setdefault(bucket, {})
        return self.state[level_name][bucket]

    def has_level(self, level_name):
        return level_name in self.state

    def get_bucket(self, level_name: str, bucket: str) -> dict:
        return self._bucket(level_name, bucket)

    def load_bool(self, level_name: str, bucket: str, key, *, initial: bool | None = None) -> bool:
        values = self._bucket(level_name, bucket)
        if key in values:
            return bool(values[key])

        values[key] = bool(initial)
        return values[key]

    def set_bool(self, level_name: str, bucket: str, key, value: bool) -> bool:
        values = self._bucket(level_name, bucket)
        values[key] = bool(value)
        return values[key]

    def toggle_bool(self, level_name: str, bucket: str, key) -> bool:
        values = self._bucket(level_name, bucket)
        values[key] = not bool(values[key])
        return values[key]


class StatisticsState:
    def __init__(self, statistics, progress):
        self.statistics = statistics
        self.progress = progress

    def increase_progress(self):
        self.progress += 1

    def update_kill_statistics(self, enemy):
        self.statistics['kill'].setdefault(enemy, 0)
        self.statistics['kill'][enemy] += 1

    def update_statistic(self, key):
        self.statistics[key] += 1


class DialogueState:
    def __init__(self, dialogue):
        self.dialogue = dialogue

    def get_bucket(self, speaker_id: str) -> dict:
        bucket = self.dialogue.setdefault(speaker_id, {})
        bucket.setdefault('progress', {})
        bucket.setdefault('consumed', {})
        return bucket

    def get_progress(self, speaker_id: str, node_id: str) -> int:
        bucket = self.get_bucket(speaker_id)
        return int(bucket['progress'].get(node_id, 0))

    def set_progress(self, speaker_id: str, node_id: str, progress: int):
        bucket = self.get_bucket(speaker_id)
        bucket['progress'][node_id] = int(progress)

    def reset_progress(self, speaker_id: str, node_id: str):
        bucket = self.get_bucket(speaker_id)
        bucket['progress'].pop(node_id, None)

    def is_consumed(self, speaker_id: str, node_id: str) -> bool:
        bucket = self.get_bucket(speaker_id)
        return bool(bucket['consumed'].get(node_id, False))

    def consume(self, speaker_id: str, node_id: str):
        bucket = self.get_bucket(speaker_id)
        bucket['consumed'][node_id] = True

class NarrativeState:
    QUEST_INACTIVE = 'inactive'
    QUEST_ACTIVE = 'active'
    QUEST_COMPLETED = 'completed'
    QUEST_FAILED = 'failed'

    def __init__(self, *, events, quests, cutscenes_complete, defeated_bosses, dialogue):
        self.events = events
        self.quests = quests
        self.cutscenes_complete = cutscenes_complete
        self.defeated_bosses = defeated_bosses
        self.dialogue = DialogueState(dialogue)

    def mark_cutscene_complete(self, cutscene_name):
        self.cutscenes_complete[cutscene_name] = True

    def update_event(self, event_name):
        self.events[event_name] = True

    def mark_boss_defeated(self, boss_id):
        self.defeated_bosses[boss_id] = True

    def is_boss_defeated(self, boss_id):
        return self.defeated_bosses.get(boss_id, False)

    def is_event_complete(self, event_name):
        return self.events.get(event_name, False)

    def is_cutscene_complete(self, cutscene_name):
        return self.cutscenes_complete.get(cutscene_name, False)

    def get_quest_status(self, quest_name):
        return self.quests.get(quest_name, self.QUEST_INACTIVE)

    def set_quest_status(self, quest_name, status):
        if status not in {
            self.QUEST_INACTIVE,
            self.QUEST_ACTIVE,
            self.QUEST_COMPLETED,
            self.QUEST_FAILED,
        }:
            raise ValueError(f"Invalid quest status '{status}' for '{quest_name}'.")
        self.quests[quest_name] = status
        return status

    def is_quest_active(self, quest_name):
        return self.get_quest_status(quest_name) == self.QUEST_ACTIVE

    def is_quest_completed(self, quest_name):
        return self.get_quest_status(quest_name) == self.QUEST_COMPLETED

    def is_quest_failed(self, quest_name):
        return self.get_quest_status(quest_name) == self.QUEST_FAILED

class World_state():
    QUEST_INACTIVE = NarrativeState.QUEST_INACTIVE
    QUEST_ACTIVE = NarrativeState.QUEST_ACTIVE
    QUEST_COMPLETED = NarrativeState.QUEST_COMPLETED
    QUEST_FAILED = NarrativeState.QUEST_FAILED

    def __init__(self, game_objects):
        self.game_objects = game_objects
        save = read_files.read_json("saves/slots/slot1/save.json")

        self.objects = WorldObjectState(save['world_state'])
        self.statistics_state = StatisticsState(
            save.get('statistics', {'kill': {}, 'amber_droplet': 0, 'death': 0}),
            save.get('progress', 1),
        )
        self.narrative = NarrativeState(
            events=save.get('events', {}),
            quests=save.get('quests', {}),
            cutscenes_complete=save.get('cutscenes_complete', {}),
            defeated_bosses=save.get('defeated_bosses', {}),
            dialogue=save.get('dialogue', {}),
        )
