from gameplay.sequences import BossEncounter, ButterflyEncounter, CultistEncounter, DeerEncounter, DeathSequence, DefeatedBoss, StartGame


REGISTER_SEQUENCES = {
    'boss_encounter': BossEncounter,
    'butterfly_encounter': ButterflyEncounter,
    'cultist_encounter': CultistEncounter,
    'deer_encounter': DeerEncounter,
    'death': DeathSequence,
    'defeated_boss': DefeatedBoss,
    'start_game': StartGame,
}
