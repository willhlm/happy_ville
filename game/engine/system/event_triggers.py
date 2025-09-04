import pygame
from gameplay.entities.entities import Interactable

class Event_trigger(Interactable):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.event = kwarg.get('event', False)
        self.new_state = kwarg.get('new_state', False)#if it is an event that requires new sttae, e.g. cutscene

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        if self.new_state:#if it is an event that requires new sttae, e.g. cutscene            
            if self.event == 'Butterfly_encounter':
                if not self.game_objects.world_state.statistics['kill'].get('maggot',False): return#don't do cutscene if aggro path is not chosen

            self.game_objects.game.state_manager.enter_state(self.event.capitalize(), category = 'game_states_cutscenes')              
        else:            
            self.game_objects.quests_events.initiate_event(self.event.capitalize())#event
        
        self.kill()#is this a problem in re-spawn?

class Start_larv_party(Event_trigger):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def player_collision(self, player):
        if self.game_objects.world_state.quests.get('larv_party', False): return#completed, return
        if self.game_objects.quests_events.active_quests.get('larv_party', False):
            if self.game_objects.quests_events.active_quests['larv_party'].running: return
            self.game_objects.quests_events.active_quests['larv_party'].initiate_quest()
        else:
            self.game_objects.quests_events.initiate_quest('larv_party')        

class Stop_larv_party(Event_trigger):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def player_collision(self, player):
        if not self.game_objects.quests_events.active_quests.get('larv_party', False): return
        if not self.game_objects.quests_events.active_quests['larv_party'].running: return#if quest is not running
        self.game_objects.quests_events.active_quests['larv_party'].pause_quest()