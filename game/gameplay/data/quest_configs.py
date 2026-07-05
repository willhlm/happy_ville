from engine.utils import read_files

DATA_DIR = "gameplay/data/quests"
_CACHE = {}


def get_quest_config(quest_id):
    if quest_id not in _CACHE:
        _CACHE[quest_id] = read_files.read_json(f"{DATA_DIR}/{quest_id}.json")
    return _CACHE[quest_id]
