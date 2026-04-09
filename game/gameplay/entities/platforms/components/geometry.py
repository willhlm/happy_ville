from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CollisionSample:
    side: str
    position: float
    collider: object
    source: object
    collision_kind: str = 'block'
    clamp_floor: bool = False
