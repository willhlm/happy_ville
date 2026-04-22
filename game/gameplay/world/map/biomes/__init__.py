from .base import Biome
from .crystal_mines import Crystal_mines
from .dark_forest import Dark_forest
from .golden_fields import Golden_fields
from .hlifblom import Hlifblom
from .nordveden import Nordveden
from .rhoutta_encounter import Rhoutta_encounter
from .tall_trees import Tall_trees
from .village import Village
from .wakeup_forest import Wakeup_forest

_BIOME_REGISTRY = {
    "village": Village,
    "nordveden": Nordveden,
    "rhoutta_encounter": Rhoutta_encounter,
    "hlifblom": Hlifblom,
    "golden_fields": Golden_fields,
    "crystal_mines": Crystal_mines,
    "dark_forest": Dark_forest,
    "tall_trees": Tall_trees,
    "wakeup_forest": Wakeup_forest,
}


def get_biome_cls(biome_name: str):
    return _BIOME_REGISTRY.get(biome_name, Biome)


__all__ = [
    "Biome",
    "Village",
    "Nordveden",
    "Rhoutta_encounter",
    "Hlifblom",
    "Golden_fields",
    "Crystal_mines",
    "Dark_forest",
    "Tall_trees",
    "Wakeup_forest",
    "get_biome_cls",
]
