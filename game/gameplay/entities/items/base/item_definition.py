from dataclasses import dataclass


@dataclass(frozen=True)
class ItemDefinition:
    item_id: str
    description: str = ''
    inventory_animation_name: str = 'idle'
    pickup_text: str = ''
    pickup_ui_image_path: str = ''
