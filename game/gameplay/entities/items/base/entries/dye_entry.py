from dataclasses import dataclass


@dataclass
class DyeEntry:
    name: str
    image: object
    channel: str
    target_colour: list
    replace_colour: list

    @classmethod
    def from_world_item(cls, item):
        return cls(
            name=item.name,
            image=item.image,
            channel=item.channel,
            target_colour=item.target_colour,
            replace_colour=item.replace_colour,
        )
