from engine.utils import read_files

DATA_DIR = "gameplay/data/narration"


def get_narration_config(narration_id):
    return read_files.read_json(f"{DATA_DIR}/{narration_id}.json")
