from engine.utils import read_files

DATA_DIR = 'gameplay/data/boss_encounters'
_CACHE = {}


def get_boss_encounter_config(encounter_id):
    if encounter_id not in _CACHE:
        _CACHE[encounter_id] = read_files.read_json(f'{DATA_DIR}/{encounter_id}.json')
    return _CACHE[encounter_id]
