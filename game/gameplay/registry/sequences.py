from gameplay.sequences import BossEncounter, ButterflyEncounter, CultistEncounter, DeerEncounter, DeathSequence, DefeatedBoss, LiftTraversalSequence, MapTraversalSequence, StartGame


REGISTER_SEQUENCES = {
    'boss_encounter': BossEncounter,
    'butterfly_encounter': ButterflyEncounter,
    'cultist_encounter': CultistEncounter,
    'deer_encounter': DeerEncounter,
    'death': DeathSequence,
    'defeated_boss': DefeatedBoss,
    'lift_traversal': LiftTraversalSequence,
    'map_traversal': MapTraversalSequence,
    'start_game': StartGame,
}
