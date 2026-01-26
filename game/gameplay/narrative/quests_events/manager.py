class QuestsEventsManager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_quests = {}#Long-term objective (fetch, kill, story arc)
        self.active_events = {}#One-shot gameplay moment (ambush, miniboss, cutscene trigger)

    def initiate_quest(self, quest, **kwarg):
        if not self.active_quests.get(quest, False):#if it is the first time getting the quest
            self.active_quests[quest] = self.game_objects.registry.fetch('events', quest)(self.game_objects, **kwarg)            
        self.active_quests[quest].initiate_quest()#if it alraedy exits, re initate it
       
    def initiate_event(self, event, **kwarg):#events e.g. encounters: probably don't need to save all of them
        self.active_events[event] = self.game_objects.registry.fetch('events', event)(self.game_objects, **kwarg)

