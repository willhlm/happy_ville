import pygame
from .base_collisions import BaseCollisions

class EventTrigger(BaseCollisions):
    blocks_on_flow_complete = True#if the event was shot once, block it
    blocks_on_event_complete = False#if the event was completed, block the event trigger

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.event = kwarg.get('event', False)
        self.ID = kwarg.get('ID', False)
        self.kwarg = kwarg

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
            
        if self.ID and self.game_objects.world_state.narrative.is_flow_complete(self.ID):
            self.kill()
            return

        if self.game_objects.registry.fetch('sequences', self.event):#is it a sequence?
            self.game_objects.sequence_manager.start_sequence(self.event, **self.kwarg)
        elif self._is_registered_state():#is it a new satte
            self.game_objects.game.state_manager.enter_state(self.event, **self.kwarg)
        else:#is it an event?
            self.game_objects.quests_events.initiate_event(self.event)

        self.kill()

    def _is_registered_state(self):
        return self.game_objects.game.state_manager.has_state(self.event)

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('ID', kwarg['event'])

class ButterflyEncounter(EventTrigger):
    blocks_on_event_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if not self.game_objects.world_state.statistics_state.statistics['kill'].get('maggot',False): return#don't do cutscene if aggro path is not chosen
        self.game_objects.sequence_manager.start_sequence(self.event)
        
class StartLarvParty(EventTrigger):
    blocks_on_event_complete = False

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.game_objects.world_state.narrative.is_quest_completed('larv_party'): return#completed, return
        if self.game_objects.quests_events.active_quests.get('larv_party', False):
            if self.game_objects.quests_events.active_quests['larv_party'].running: return
            self.game_objects.quests_events.active_quests['larv_party'].initiate_quest()
        else:
            self.game_objects.quests_events.initiate_quest('larv_party')        

class StopLarvParty(EventTrigger):
    blocks_on_event_complete = False

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if not self.game_objects.quests_events.active_quests.get('larv_party', False): return
        if not self.game_objects.quests_events.active_quests['larv_party'].running: return#if quest is not running
        self.game_objects.quests_events.active_quests['larv_party'].pause_quest()

class MiniBoss(EventTrigger):   
    ''' a general mini boss system'''
    blocks_on_event_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.boss_id = f"{game_objects.map.level_name}_{int(pos[0])}_{int(pos[1])}"

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.game_objects.world_state.narrative.is_boss_defeated(self.boss_id): return#if the boss has been defeated
        self.game_objects.quests_events.initiate_event('mini_boss', boss_id = self.boss_id)             
        self.kill()           

class Narration(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.start_index = int(kwarg.get('start_index', 0))
        self.count = int(kwarg.get('count', 2))
        self.text_key = kwarg.get('text', 'intro_lore')
        self.mode = kwarg.get('mode', 'sequential')

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player':
            return

        self.game_objects.ui.overlay.play_text_block(
            self.game_objects,
            self.text_key,
            start_index=self.start_index,
            count=self.count,
            mode=self.mode,
            channel="narration",
        )

        self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('text', kwarg.get('ID', kwarg['event']))

class BossEncounter(BaseCollisions):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.ID = kwarg.get('ID', False)
        self.kwarg = kwarg
        self.event = kwarg.get('event', 'boss_encounter')

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return#only player trigger
        if self.ID and self.game_objects.world_state.narrative.is_boss_defeated(self.ID):
            self.kill()
            return

        if not self.game_objects.world_state.narrative.is_flow_complete(self.ID):
            kwarg = dict(self.kwarg)
            if self.ID:
                kwarg['entity'] = self.game_objects.map.ctx.references[self.ID]
            self.game_objects.sequence_manager.start_sequence(self.event, **kwarg)
        self.kill()
