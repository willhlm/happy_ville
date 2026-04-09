import math
import pygame
import random

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class InteractableVines(Interactables):#issue when player lands on a bent vine, and the bottom hitbox will "hook" it
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict(
            'assets/sprites/entities/interactables/vines/nordveden/vines_1/',
            game_objects,
        )
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

        self.body_width = max(8.0, self.rect.width * 0.02)
        self.body_left_px = (self.rect.width - self.body_width) * 0.5
        self.body_right_px = self.body_left_px + self.body_width

        self.hitbox = self.rect.copy()

        self.time = 0
        self.offset = random.uniform(0.0, 10.0)

        self.anchor = [self.rect.midtop[0], self.rect.top]
        self.point_count = max(8, min(18, self.rect.height // 6))
        self.segment_length = self.rect.height / max(1, self.point_count - 1)
        self.idle_constraint_iterations = 4
        self.active_constraint_iterations = 8
        self.damping = 0.92
        self.gravity = 0.2
        self.wind_strength = 0.1
        self.collision_padding = max(1.5, self.body_width * 0.08)
        self.surface_snap_padding = max(1.0, self.body_width * 0.12)
        self.colliders = {}
        self.is_colliding = False

        self.points = []
        self.prev_points = []
        self.section_vertices = []
        self._init_chain()
        self._init_sections()

        self.hit_component.set_invinsibility(True)    

    def _init_chain(self):
        self.points.clear()
        self.prev_points.clear()

        for index in range(self.point_count):
            point = [self.anchor[0], self.anchor[1] + index * self.segment_length]
            self.points.append(point[:])
            self.prev_points.append(point[:])

    def _init_sections(self):
        self.section_vertices.clear()
        segment_height = self.image.height / max(1, self.point_count - 1)
        for index in range(self.point_count - 1):
            source_top = segment_height * index
            source_bottom = segment_height * (index + 1)
            self.section_vertices.append([
                (self.body_left_px, source_top),
                (self.body_right_px, source_top),
                (self.body_left_px, source_bottom),
                (self.body_right_px, source_bottom),
            ])

    def _integrate(self, dt):
        dt_scale = max(0.5, min(dt, 2.0))

        for index in range(1, self.point_count):
            point = self.points[index]
            previous = self.prev_points[index]

            velocity_x = (point[0] - previous[0]) * self.damping
            velocity_y = (point[1] - previous[1]) * self.damping
            previous[0], previous[1] = point[0], point[1]

            height_weight = index / max(1, self.point_count - 1)
            wind = math.sin(self.time * 0.04 + self.offset + index * 0.55) * self.wind_strength * height_weight

            point[0] += velocity_x + wind * dt_scale
            point[1] += velocity_y + self.gravity * dt_scale

    def _solve_constraints(self):
        self.points[0][0] = self.anchor[0]
        self.points[0][1] = self.anchor[1]

        for index in range(self.point_count - 1):
            point_a = self.points[index]
            point_b = self.points[index + 1]

            delta_x = point_b[0] - point_a[0]
            delta_y = point_b[1] - point_a[1]
            distance = math.hypot(delta_x, delta_y)
            if distance == 0:
                continue

            difference = (distance - self.segment_length) / distance
            correction_x = delta_x * difference
            correction_y = delta_y * difference

            if index == 0:
                point_b[0] -= correction_x
                point_b[1] -= correction_y
                continue

            point_a[0] += correction_x * 0.5
            point_a[1] += correction_y * 0.5
            point_b[0] -= correction_x * 0.5
            point_b[1] -= correction_y * 0.5

    def _resolve_collision_axis(self, point, previous, collider):
        crossed_top = previous[1] <= collider.top < point[1]
        crossed_bottom = previous[1] >= collider.bottom > point[1]
        crossed_left = previous[0] <= collider.left < point[0]
        crossed_right = previous[0] >= collider.right > point[0]

        if crossed_top:
            return 'top'
        if crossed_bottom:
            return 'bottom'
        if crossed_left:
            return 'left'
        if crossed_right:
            return 'right'

        overlaps = {
            'left': abs(point[0] - collider.left),
            'right': abs(collider.right - point[0]),
            'top': abs(point[1] - collider.top),
            'bottom': abs(collider.bottom - point[1]),
        }
        return min(overlaps, key=overlaps.get)

    def _solve_body_collision(self, collision_data):
        collider = collision_data['collider']
        player_hitbox = collision_data['player_hitbox']
        collider_velocity = collision_data['velocity']
        side_offset = self.body_width * 0.5 + self.collision_padding
        for index in range(1, self.point_count):
            point = self.points[index]
            previous = self.prev_points[index]
            if not collider.collidepoint(point[0], point[1]):
                continue

            collision_axis = self._resolve_collision_axis(point, previous, collider)

            if collision_axis == 'top':
                point[1] = player_hitbox.top - self.surface_snap_padding
                previous[1] = point[1]
                point[0] += collider_velocity[0]
                previous[0] = point[0] - collider_velocity[0] * 0.25
            elif collision_axis == 'bottom':
                point[1] = player_hitbox.bottom + self.surface_snap_padding
                previous[1] = point[1]
            elif collision_axis == 'left':
                point[0] = player_hitbox.left - side_offset
                previous[0] = point[0]
            else:
                point[0] = player_hitbox.right + side_offset
                previous[0] = point[0]

    def _track_collider(self, entity):
        if not hasattr(entity, 'hitbox'):
            return

        pad_x = self.body_width + self.collision_padding * 2
        player_hitbox = entity.hitbox.copy()
        collider = entity.hitbox.inflate(pad_x, 0)
        previous_data = self.colliders.get(entity)
        if previous_data is None:
            velocity = [0.0, 0.0]
        else:
            prev_collider = previous_data['collider']
            velocity = [
                collider.centerx - prev_collider.centerx,
                collider.centery - prev_collider.centery,
            ]

        self.colliders[entity] = {
            'player_hitbox': player_hitbox,
            'collider': collider,
            'velocity': velocity,
        }

    def collision(self, entity):
        self._track_collider(entity)
        self.is_colliding = bool(self.colliders)

    def on_collision(self, entity):
        pass

    def take_dmg(self, damage):
        pass

    def on_noncollision(self, entity):
        self.colliders.pop(entity, None)
        self.is_colliding = bool(self.colliders)

    def update(self, dt):
        self.time += dt
        self._integrate(dt)
        iterations = self.active_constraint_iterations if self.is_colliding else self.idle_constraint_iterations
        for _ in range(iterations):
            self._solve_constraints()
            if self.is_colliding:
                for collision_data in self.colliders.values():
                    self._solve_body_collision(collision_data)

    def _segment_vertices(self, top_point, bottom_point, scroll):
        delta_x = bottom_point[0] - top_point[0]
        delta_y = bottom_point[1] - top_point[1]
        length = max(0.001, math.hypot(delta_x, delta_y))

        left_normal_x = -delta_y / length
        left_normal_y = delta_x / length
        half_width = self.body_width * 0.5

        bottom_right = (
            bottom_point[0] - left_normal_x * half_width - scroll[0],
            bottom_point[1] - left_normal_y * half_width - scroll[1],
        )
        bottom_left = (
            bottom_point[0] + left_normal_x * half_width - scroll[0],
            bottom_point[1] + left_normal_y * half_width - scroll[1],
        )
        top_left = (
            top_point[0] + left_normal_x * half_width - scroll[0],
            top_point[1] + left_normal_y * half_width - scroll[1],
        )
        top_right = (
            top_point[0] - left_normal_x * half_width - scroll[0],
            top_point[1] - left_normal_y * half_width - scroll[1],
        )
        return [bottom_right, bottom_left, top_left, top_right]

    def draw(self, target):
        scroll = self.game_objects.camera_manager.camera.interp_scroll

        for index in range(self.point_count - 1):
            top_point = self.points[index]
            bottom_point = self.points[index + 1]
            dest_vertices = self._segment_vertices(top_point, bottom_point, scroll)

            self.game_objects.game.display.render_from_vertices(
                self.image,
                target,
                dest_vertices,
                self.section_vertices[index],
            )
