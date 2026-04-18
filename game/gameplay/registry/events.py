from gameplay.narrative.quests_events.events import (
    AcidEscape,
    ButterflyEncounter,
    CultistEncounter,
    GoldenFieldsEncounter1,
    MiniBoss,
)

REGISTER_EVENTS = {
    'mini_boss': MiniBoss,
    'golden_fields_encounter_1': GoldenFieldsEncounter1,
    'acid_escape': AcidEscape,
    'cultist_encounter': CultistEncounter,
    'butterfly_encounter': ButterflyEncounter,
}
