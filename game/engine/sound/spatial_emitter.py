from __future__ import annotations

import math
import pygame
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from engine.utils.functions import track_distance
from .spatial_spaces import ParallaxScreenSpace

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
    listener_transform: Callable[[Vec2], Vec2] = field(default=lambda p: p)

class SpatialAudioSystem:
    """Owns spatial emitters and updates their volumes each frame.

    Registration examples:
        World-space point emitter:
            sound.register_spatial_point(
                sound=sfx,
                get_point=lambda: entity.hitbox.center,
            )

        Parallax rect emitter:
            sound.register_spatial_rect(
                sound=sfx,
                get_rect=lambda: entity.rect,
                parallax=entity.parallax,
            )

        Custom transformed point emitter:
            my_space = ParallaxScreenSpace(
                lambda: game_objects.camera_manager.camera.interp_scroll,
                entity.parallax,
            )
            sound.register_spatial_point(
                sound=sfx,
                get_point=lambda: entity.rect.center,
                listener_transform=my_space.listener_point,
                source_transform=my_space.point,
            )

        Custom transformed rect emitter:
            my_space = ParallaxScreenSpace(
                lambda: game_objects.camera_manager.camera.interp_scroll,
                entity.parallax,
            )
            sound.register_spatial_rect(
                sound=sfx,
                get_rect=lambda: entity.rect,
                listener_transform=my_space.listener_point,
                source_transform=my_space.rect,
            )

    """
    def __init__(self, play_sfx_fn: Callable[..., pygame.mixer.Channel], camera_scroll_getter=None):
        """
        play_sfx_fn must be something like:
            play_sfx_fn(sound, loops=-1, volume=0.0, fade_ms=0) -> pygame.mixer.Channel
        """
        self._play_sfx = play_sfx_fn
        self._emitters = {}
        self._next_id = 1
        self._camera_scroll_getter = camera_scroll_getter
        self._listener_pos = None

    def _resolve_space(self, parallax, listener_transform, source_transform, source_kind):
        if parallax is None:
            return listener_transform, source_transform

        if self._camera_scroll_getter is None:
            raise RuntimeError("SpatialAudioSystem requires a camera scroll getter before using parallax emitters.")

        space = ParallaxScreenSpace(self._camera_scroll_getter, parallax)
        default_source_transform = space.rect if source_kind == 'rect' else space.point
        return (
            listener_transform or space.listener_point,
            source_transform or default_source_transform,
        )

    def register_point(self, sound, get_point, *, base_volume=0.3, loops=-1, fade_ms=0, min_dist=48, max_dist=300, listener_transform=None, source_transform=None, parallax=None):
        listener_transform, source_transform = self._resolve_space(parallax, listener_transform, source_transform, source_kind='point')
        if listener_transform is None:
            listener_transform = lambda p: p
        if source_transform is None:
            source_transform = lambda value: value

        channel = self._play_sfx(sound, loops=loops, volume=0.0, fade_ms=fade_ms)
        eid = self._next_id; self._next_id += 1

        self._emitters[eid] = SpatialEmitter(
            emitter_id=eid,
            channel=channel,
            get_pos2=lambda _listener_pos: source_transform(get_point()),
            base_volume=base_volume,
            min_dist=min_dist,
            max_dist=max_dist,
            listener_transform=listener_transform,
        )
        return eid


    def register_rect(self, sound, get_rect, *, base_volume=0.5, loops=-1, fade_ms=0, min_dist=96, max_dist=600, listener_transform=None, source_transform=None, parallax=None):
        listener_transform, source_transform = self._resolve_space(parallax, listener_transform, source_transform, source_kind='rect')
        if listener_transform is None:
            listener_transform = lambda p: p
        if source_transform is None:
            source_transform = lambda value: value

        channel = self._play_sfx(sound, loops=loops, volume=0.0, fade_ms=fade_ms)
        eid = self._next_id; self._next_id += 1

        self._emitters[eid] = SpatialEmitter(
            emitter_id=eid,
            channel=channel,
            get_pos2=lambda listener_pos: _closest_point_on_rect(listener_pos, source_transform(get_rect())),
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

    def clear(self, *, fade_ms: int = 0) -> None:
        for emitter_id in list(self._emitters.keys()):
            self.unregister(emitter_id, fade_ms=fade_ms)

    def play_point(self, sound, point, *, volume=1.0, loops=0, fade_ms=0, min_dist=48, max_dist=300, listener_pos=None, listener_transform=None, source_transform=None, parallax=None):
        listener_pos = listener_pos or self._listener_pos
        if listener_pos is None:
            return self._play_sfx(sound, loops=loops, volume=volume, fade_ms=fade_ms)

        listener_transform, source_transform = self._resolve_space(parallax, listener_transform, source_transform, source_kind='point')
        if listener_transform is None:
            listener_transform = lambda p: p
        if source_transform is None:
            source_transform = lambda value: value

        effective_listener = listener_transform(listener_pos)
        source_point = source_transform(point)
        amp = track_distance(effective_listener, source_point, r0=max_dist, r1=min_dist)
        if amp <= 0:
            return None

        return self._play_sfx(sound, loops=loops, volume=volume * amp, fade_ms=fade_ms)

    def update(self, listener_pos: Vec2) -> None:
        self._listener_pos = listener_pos
        if not self._emitters:
            return

        dead = []
        for eid, emitter in list(self._emitters.items()):
            try:
                if not emitter.channel.get_busy():
                    dead.append(eid)
                    continue

                lpos = emitter.listener_transform(listener_pos)
                pos2 = emitter.get_pos2(lpos)
                amp = track_distance(lpos, pos2, r0=emitter.max_dist, r1=emitter.min_dist)
                emitter.channel.set_volume(emitter.base_volume * amp)

            except Exception:
                dead.append(eid)

        for eid in dead:
            self._emitters.pop(eid, None)
