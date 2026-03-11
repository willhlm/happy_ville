from __future__ import annotations

import math
import pygame
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

from engine.utils.functions import track_distance

Vec2 = Tuple[float, float]

def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v

def _closest_point_on_rect(p: Vec2, r: pygame.Rect) -> Vec2:
    px, py = p
    #pygame.Rect.right/bottom are edge coords; clamp is fine for distance purposes
    cx = _clamp(px, r.left, r.right)
    cy = _clamp(py, r.top, r.bottom)
    return (cx, cy)

@dataclass
class SpatialEmitter:
    emitter_id: int
    channel: pygame.mixer.Channel
    get_pos2: Callable[[Vec2], Vec2]
    base_volume: float
    min_dist: float
    max_dist: float
    listener_transform: Callable[[Vec2], Vec2] = field(default=lambda p: p)  # NEW

class SpatialAudioSystem:
    """Owns spatial emitters and updates their volumes each frame."""
    def __init__(self, play_sfx_fn: Callable[..., pygame.mixer.Channel]):
        """
        play_sfx_fn must be something like:
            play_sfx_fn(sound, loops=-1, volume=0.0, fade_ms=0) -> pygame.mixer.Channel
        """
        self._play_sfx = play_sfx_fn
        self._emitters = {}
        self._next_id = 1

    def register_point(self, sound, get_point, *, base_volume=0.3, loops=-1, fade_ms=0, min_dist=48, max_dist=300, listener_transform=None):
        if listener_transform is None:
            listener_transform = lambda p: p

        channel = self._play_sfx(sound, loops=loops, volume=0.0, fade_ms=fade_ms)
        eid = self._next_id; self._next_id += 1

        self._emitters[eid] = SpatialEmitter(
            emitter_id=eid,
            channel=channel,
            get_pos2=lambda _listener_pos: get_point(),
            base_volume=base_volume,
            min_dist=min_dist,
            max_dist=max_dist,
            listener_transform=listener_transform,
        )
        return eid


    def register_rect(self, sound, get_rect, *, base_volume=0.5, loops=-1, fade_ms=0, min_dist=96, max_dist=600, listener_transform=None):
        if listener_transform is None:
            listener_transform = lambda p: p

        channel = self._play_sfx(sound, loops=loops, volume=0.0, fade_ms=fade_ms)
        eid = self._next_id; self._next_id += 1

        self._emitters[eid] = SpatialEmitter(
            emitter_id=eid,
            channel=channel,
            get_pos2=lambda listener_pos: _closest_point_on_rect(listener_pos, get_rect()),
            base_volume=base_volume,
            min_dist=min_dist,
            max_dist=max_dist,
            listener_transform=listener_transform,
        )
        return eid

    def unregister(self, emitter_id: int, *, fade_ms: int = 200) -> None:
        emitter = self._emitters.pop(emitter_id, None)
        if not emitter:
            return
        try:
            if fade_ms and fade_ms > 0:
                emitter.channel.fadeout(fade_ms)
            else:
                emitter.channel.stop()
        except Exception:
            pass

    def update(self, listener_pos: Vec2) -> None:
        if not self._emitters:
            return

        dead = []
        for eid, emitter in list(self._emitters.items()):
            try:
                if not emitter.channel.get_busy():
                    dead.append(eid)
                    continue

                lpos = emitter.listener_transform(listener_pos)   # NEW: convert listener to emitter space
                pos2 = emitter.get_pos2(lpos)
                amp = track_distance(lpos, pos2, r0=emitter.max_dist, r1=emitter.min_dist)
                emitter.channel.set_volume(emitter.base_volume * amp)

            except Exception:
                dead.append(eid)

        for eid in dead:
            self._emitters.pop(eid, None)