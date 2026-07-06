from engine.utils import read_files

DATA_DIR = "gameplay/data/gauntlets"
_CACHE = {}


def get_gauntlet_config(gauntlet_id):
    if gauntlet_id not in _CACHE:
        _CACHE[gauntlet_id] = read_files.read_json(f"{DATA_DIR}/{gauntlet_id}.json")
    return _CACHE[gauntlet_id]
