import re

class QuestsEventsManager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_quests = {}#Long-term objective (fetch, kill, story arc)
        self.active_events = {}#One-shot gameplay moment (ambush, miniboss, cutscene trigger)

    def _normalize_key(self, key):
        if not isinstance(key, str):
            raise TypeError("Quest/event keys must be strings.")
        normalized = re.sub(r'(?<!^)(?=[A-Z])', '_', key).replace('-', '_').lower()
        return normalized

    def initiate_quest(self, quest, **kwarg):
        quest_key = self._normalize_key(quest)
        if not self.active_quests.get(quest_key, False):#if it is the first time getting the quest
            quest_class = self.game_objects.registry.fetch('quests', quest_key)
            if quest_class is None:
                raise KeyError(f"Unknown quest '{quest_key}'.")
            self.active_quests[quest_key] = quest_class(self.game_objects, **kwarg)
        self.active_quests[quest_key].initiate_quest()#if it alraedy exits, re initate it
       
    def initiate_event(self, event, **kwarg):#events e.g. encounters: probably don't need to save all of them
        event_key = self._normalize_key(event)
        event_class = self.game_objects.registry.fetch('events', event_key)
        if event_class is None:
            raise KeyError(f"Unknown event '{event_key}'.")
        self.active_events[event_key] = event_class(self.game_objects, **kwarg)
