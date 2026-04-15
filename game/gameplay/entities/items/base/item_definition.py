from dataclasses import dataclass


@dataclass(frozen=True)
class ItemDefinition:
    item_id: str | None = None
    description: str = ''
    inventory_animation_name: str = 'idle'
    pickup_persistence_key: str | None = None

