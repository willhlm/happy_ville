from engine.utils import read_files

DATA_DIR = "gameplay/data/ui_overlays"


def get_ui_overlay_config(overlay_id):
    return read_files.read_json(f"{DATA_DIR}/{overlay_id}.json")
