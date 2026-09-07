"""Reusable, entity-owned sound event playback."""

from __future__ import annotations

from dataclasses import dataclass
from random import choice


@dataclass(frozen=True)
class SoundEvent:
    """How an entity event maps to one of its owned sound assets."""

    sound_key: str
    relative_volume: float = 1.0


class EntityAudioComponent:
    """Play named events using an entity's sound assets through ``GameAudio``.

    The entity retains ownership of its clips and authored relative volumes.  This
    component only selects a clip and sends it through the central audio path.
    """

    def __init__(self, entity, events):
        self.entity = entity
        self.events = events

    def play(self, event_name, *, loop=0, fade=0, volume_multiplier=1.0):
        event = self.events[event_name]
        clips = self.entity.sounds[event.sound_key]
        sound = choice(clips)

        return self.entity.game_objects.sound.play_sfx(
            sound,
            loop=loop,
            vol=event.relative_volume * volume_multiplier,
            fade=fade,
        )
