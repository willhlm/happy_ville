import random
from engine.utils import read_files

CATEGORY_PRIORITY = {
    'quest': 300,
    'reactive': 200,
    'ambient': 100,
    'fallback': 0,
}

class Conversation():
    def __init__(self,entity):
        self.entity = entity
        self.active_node_id = None

    def start_conversation(self):
        node = self._select_active_node()
        if not node:
            self.active_node_id = None
            return None

        self.active_node_id = node['id']
        return self._line_for_node(node)

    def advance_conversation(self):
        if not self.active_node_id:
            return None

        node = self.nodes_by_id[self.active_node_id]
        speaker_id = self._speaker_id()
        progress = self.entity.game_objects.world_state.narrative.dialogue.get_progress(speaker_id, node['id']) + 1

        if progress >= len(node['lines']):
            self.entity.game_objects.world_state.narrative.dialogue.reset_progress(speaker_id, node['id'])
            if node.get('once', False):
                self.entity.game_objects.world_state.narrative.dialogue.consume(speaker_id, node['id'])
            self.active_node_id = None
            return None

        self.entity.game_objects.world_state.narrative.dialogue.set_progress(speaker_id, node['id'], progress)
        return node['lines'][progress]

    def _speaker_id(self):
        return self.entity.name

    def _line_for_node(self, node):
        progress = self.entity.game_objects.world_state.narrative.dialogue.get_progress(self._speaker_id(), node['id'])
        if progress >= len(node['lines']):
            self.entity.game_objects.world_state.narrative.dialogue.reset_progress(self._speaker_id(), node['id'])
            progress = 0
        return node['lines'][progress]

    def _select_active_node(self):
        world_state = self.entity.game_objects.world_state
        candidates = []
        for node in self.nodes:
            if node.get('once', False) and world_state.narrative.dialogue.is_consumed(self._speaker_id(), node['id']):
                continue
            if self._conditions_match(node.get('conditions', [])):
                candidates.append(node)

        if not candidates:
            return None

        candidates.sort(key=self._node_sort_key)
        return candidates[0]

    def _node_sort_key(self, node):
        category = node.get('category', 'fallback')
        return (-CATEGORY_PRIORITY.get(category, 0), -node.get('priority', 0), node['id'])

    def _conditions_match(self, conditions):
        world_state = self.entity.game_objects.world_state
        for condition in conditions:
            kind = condition.get('type')
            value = condition.get('value', True)

            if kind == 'quest':
                quest_name = condition['name']
                if isinstance(value, str):
                    if world_state.narrative.get_quest_status(quest_name) != value:
                        return False
                elif bool(value):
                    if not world_state.narrative.is_quest_active(quest_name):
                        return False
                else:
                    if world_state.narrative.is_quest_active(quest_name):
                        return False
            elif kind == 'event':
                if world_state.narrative.events.get(condition['name'], False) != value:
                    return False
            elif kind == 'progress_eq':
                if world_state.statistics_state.progress != value:
                    return False
            elif kind == 'progress_at_least':
                if world_state.statistics_state.progress < value:
                    return False
            elif kind == 'progress_at_most':
                if world_state.statistics_state.progress > value:
                    return False
            else:
                return False

        return True

class Dialogue(Conversation):#handles dialoage and what to say for NPC
    def __init__(self, entity, *, data_path = None, speaker_id = None, allow_comments = True):
        super().__init__(entity)
        self.speaker_id = speaker_id or self.entity.name
        self.dialogue_data = read_files.read_json(data_path or "gameplay/narrative/text/npc/" + self.entity.name + ".json")
        self.nodes = self._build_nodes(self.dialogue_data, 'conversation_nodes', 'conversation')
        self.nodes_by_id = {node['id']: node for node in self.nodes}
        self.comment_nodes = self._build_nodes(self.dialogue_data, 'comment_nodes', 'comment') if allow_comments else []

    def _speaker_id(self):
        return self.speaker_id

    def get_comment(self):#random text bubbles
        candidates = []
        for node in self.comment_nodes:
            if node.get('once', False) and self.entity.game_objects.world_state.narrative.dialogue.is_consumed(self._speaker_id(), node['id']):
                continue
            if self._conditions_match(node.get('conditions', [])):
                candidates.append(node)

        if not candidates:
            return None

        candidates.sort(key=self._node_sort_key)
        highest_priority = self._node_sort_key(candidates[0])
        best_candidates = [node for node in candidates if self._node_sort_key(node) == highest_priority]
        node = random.choice(best_candidates)
        return random.choice(node['lines'])

    def get_comment_settings(self):
        settings = self.dialogue_data.get('comment_settings', {})
        if not isinstance(settings, dict):
            raise ValueError(f"Dialogue comment_settings for '{self.speaker_id}' must be a dict.")
        return settings

    def _build_nodes(self, dialogue_data, section_name, section_label):
        if not isinstance(dialogue_data, dict):
            raise ValueError(f"Dialogue for '{self.speaker_id}' must be a dict.")
        return self._nodes_from_data(dialogue_data.get(section_name, []), section_name, section_label)

    def _nodes_from_data(self, nodes, section_name, section_label):
        if not isinstance(nodes, list):
            raise ValueError(f"Dialogue {section_label} data for '{self.speaker_id}' must be a list in '{section_name}'.")

        built_nodes = []
        for node in nodes:
            lines = node.get('lines', [])
            category = node.get('category', 'fallback')
            if not lines:
                continue
            built_nodes.append({
                'id': node['id'],
                'category': category,
                'priority': node.get('priority', 0),
                'conditions': node.get('conditions', []),
                'once': node.get('once', False),
                'lines': list(lines),
            })
        return built_nodes
