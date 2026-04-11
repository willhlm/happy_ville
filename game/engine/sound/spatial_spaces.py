from __future__ import annotations

import pygame


class WorldSpace:
    def listener_point(self, point):
        return point

    def point(self, point):
        return point

    def rect(self, rect):
        return rect


class ParallaxScreenSpace:
    def __init__(self, get_camera_scroll, parallax):
        self._get_camera_scroll = get_camera_scroll
        self.parallax = parallax

    def listener_point(self, point):
        scroll_x, scroll_y = self._get_camera_scroll()
        return (
            point[0] - scroll_x,
            point[1] - scroll_y,
        )

    def point(self, point):
        scroll_x, scroll_y = self._get_camera_scroll()
        return (
            int(point[0] - self.parallax[0] * scroll_x),
            int(point[1] - self.parallax[1] * scroll_y),
        )

    def rect(self, rect):
        x, y = self.point(rect.topleft)
        return pygame.Rect(x, y, rect.width, rect.height)
