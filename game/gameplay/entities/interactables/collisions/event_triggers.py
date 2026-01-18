import pygame
from gameplay.entities.interactables.base.interactables import Interactables

class EventTrigger(Interactables):
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

    def update(self, dt):
        self.group_distance()

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.new_state:#if it is an event that requires new sttae, e.g. cutscene            
            self.game_objects.game.state_manager.enter_state(self.event)              
        else:            
            self.game_objects.quests_events.initiate_event(self.event.capitalize())#event
        
        self.kill()#is this a problem in re-spawn?

class ButterflyEncounter(EventTrigger):#cut scene
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if not self.game_objects.world_state.statistics['kill'].get('maggot',False): return#don't do cutscene if aggro path is not chosen
        self.game_objects.game.state_manager.enter_state(self.event)              
        
class StartLarvParty(EventTrigger):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.game_objects.world_state.quests.get('larv_party', False): return#completed, return
        if self.game_objects.quests_events.active_quests.get('larv_party', False):
            if self.game_objects.quests_events.active_quests['larv_party'].running: return
            self.game_objects.quests_events.active_quests['larv_party'].initiate_quest()
        else:
            self.game_objects.quests_events.initiate_quest('larv_party')        

class StopLarvParty(EventTrigger):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if not self.game_objects.quests_events.active_quests.get('larv_party', False): return
        if not self.game_objects.quests_events.active_quests['larv_party'].running: return#if quest is not running
        self.game_objects.quests_events.active_quests['larv_party'].pause_quest()

class MiniBoss(EventTrigger):   
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.boss_id = f"{game_objects.map.level_name}_{int(pos[0])}_{int(pos[1])}"

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.game_objects.world_state.quests.get(self.boss_id, False): return#if the boss has been defeated
        self.game_objects.quests_events.initiate_event('mini_boss', boss_id = self.boss_id)             
        self.kill()           