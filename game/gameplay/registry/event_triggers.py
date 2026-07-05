from gameplay.entities.areas.event_triggers import *

REGISTER_EVENT_TRIGGERS = {
    'default': EventTrigger,
    'acid_escape': QuestEventTrigger,
    'boss_encounter': BossEncounterTrigger,
    'cultist_encounter': QuestEventTrigger,
    'gauntlet': GauntletTrigger,
    'golden_fields_encounter_1': QuestEventTrigger,
    'narration': NarrationTrigger,
    'pause_quest': PauseQuestTrigger,
    'quest': QuestTrigger,
    'quest_event': QuestEventTrigger,
    'sequence': SequenceTrigger,
    'state': StateTrigger,
    'ui_overlay': UIOverlayTrigger,
}
