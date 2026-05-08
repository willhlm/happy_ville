import math
from dataclasses import dataclass, field


@dataclass
class StimulusSource:
    owner: object
    channel: str
    radius: float
    strength: float = 1.0
    falloff: float = 0.0
    priority: float = 0.0
    tags: set = field(default_factory=set)
    active: bool = True
    persistent: bool = False

    @property
    def position(self):
        hitbox = getattr(self.owner, 'hitbox', None)
        if hitbox is not None:
            return hitbox.center

        rect = getattr(self.owner, 'rect', None)
        if rect is not None:
            return rect.center

        return None

    def is_valid(self):
        if not self.active or self.owner is None:
            return False

        alive = getattr(self.owner, 'alive', None)
        if callable(alive) and not alive():
            return False

        return self.position is not None


class StimulusManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.sources = []

    def register_source(self, owner, channel, radius, **kwargs):
        source = StimulusSource(owner=owner, channel=channel, radius=radius, **kwargs)
        self.sources.append(source)
        return source

    def unregister_source(self, source):
        if source in self.sources:
            self.sources.remove(source)

    def clear_world(self):
        self.sources = [source for source in self.sources if source.persistent and source.is_valid()]

    def find_best_source(self, seeker, channels=None, bounds=None, channel_weights=None, tag_weights=None, exclude_owners=None):
        self._prune_sources()

        seeker_hitbox = getattr(seeker, 'hitbox', None)
        if seeker_hitbox is None:
            return None

        channel_weights = channel_weights or {}
        tag_weights = tag_weights or {}
        allowed_channels = set(channel_weights.keys()) if channel_weights else set(channels or [])
        excluded = set(exclude_owners or [])

        best_source = None
        best_score = None
        seeker_center = seeker_hitbox.center

        for source in self.sources:
            if source.owner is seeker or source.owner in excluded:
                continue
            if allowed_channels and source.channel not in allowed_channels:
                continue

            position = source.position
            if position is None:
                continue

            dx = position[0] - seeker_center[0]
            dy = position[1] - seeker_center[1]

            if bounds:
                if abs(dx) > bounds[0] or abs(dy) > bounds[1]:
                    continue

            distance = math.hypot(dx, dy)
            if distance > source.radius:
                continue

            score = source.priority + source.strength - source.falloff * distance
            score += channel_weights.get(source.channel, 0.0)
            for tag in source.tags:
                score += tag_weights.get(tag, 0.0)

            if best_score is None or score > best_score:
                best_source = source
                best_score = score

        return best_source

    def _prune_sources(self):
        self.sources = [source for source in self.sources if source.is_valid()]
