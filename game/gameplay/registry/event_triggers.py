from gameplay.entities.areas.event_triggers import *

REGISTER_EVENT_TRIGGERS = {
    'default': EventTrigger,
    'boss_encounter': BossEncounterTrigger,
    'event': GameplayEventTrigger,
    'gauntlet': GauntletTrigger,
    'narration': NarrationTrigger,
    'pause_quest': PauseQuestTrigger,
    'quest': QuestTrigger,
    'sequence': SequenceTrigger,
    'state': StateTrigger,
    'ui_overlay': UIOverlayTrigger,
}
