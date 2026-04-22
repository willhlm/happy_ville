from gameplay.entities.areas.event_triggers import *

REGISTER_EVENT_TRIGGERS = {
    'default': EventTrigger,
    'mini_boss': MiniBoss,
    'stop_larv_party': StopLarvParty,
    'start_larv_party': StartLarvParty,
    'butterfly_encounter': ButterflyEncounter,    
    'narration': Narration,    
    'boss_encounter': BossEncounter,
}
