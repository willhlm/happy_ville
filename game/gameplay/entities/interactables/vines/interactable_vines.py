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
        self.collider = None
        self.player_hitbox = None
        self.prev_collider = None
        self.collider_velocity = [0.0, 0.0]
        self.contact_release_distance = max(4.0, self.body_width * 0.75)
        self.edge_transition_distance = max(6.0, self.body_width * 1.5)
        self.top_hold_margin = max(8.0, self.body_width * 2.5)
        self.mode_switch_margin = max(6.0, self.body_width * 1.75)
        self.contact_blend = 0.35
        self.contact_modes = [0] * self.point_count
        self.is_colliding = False

        self.points = []
        self.prev_points = []
        self.section_vertices = []
        self._init_chain()
        self._init_sections()

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

    def _resolve_contact_mode(self, point, collider, player_hitbox, previous_mode):
        dist_left = abs(point[0] - collider.left)
        dist_right = abs(collider.right - point[0])

        # Sticky side guards — keep stable contacts from flipping.
        if previous_mode == -1 and point[0] <= collider.left + self.mode_switch_margin:
            return -1
        if previous_mode == 1 and point[0] >= collider.right - self.mode_switch_margin:
            return 1

        # Top-contact (mode 0) requires the point to be genuinely at or just inside
        # the real player top edge — NOT decided by a distance race against collider.top.
        # The old dist_top min() could classify mid-body and foot-level points as top
        # contacts because it used the inflated collider top, which sits above the real
        # player hitbox top.  That misclassification is what causes bent vines to hook.
        near_player_top = point[1] <= player_hitbox.top + self.segment_length
        within_top_span = (
            player_hitbox.left - self.top_hold_margin
            <= point[0]
            <= player_hitbox.right + self.top_hold_margin
        )
        if near_player_top and within_top_span:
            return 0

        if abs(dist_left - dist_right) < 2.0 and previous_mode in (-1, 1):
            return previous_mode
        return -1 if dist_left < dist_right else 1

    def _solve_body_collision(self):
        if self.collider is None or self.player_hitbox is None:
            return

        collider = self.collider
        player_hitbox = self.player_hitbox
        side_offset = self.body_width * 0.5 + self.collision_padding
        for index in range(1, self.point_count):
            point = self.points[index]
            was_in_contact = self.contact_modes[index] != 0
            inside = collider.collidepoint(point[0], point[1])

            if not inside and not was_in_contact:
                continue

            # Hard gate: a point below the player's feet has no valid contact state.
            # Chain constraints can pull lower vine points upward into the collider from
            # beneath — releasing them here immediately prevents them from being
            # misclassified and dragged up toward the player top (the hook artefact).
            if point[1] > player_hitbox.bottom + self.collision_padding:
                self.contact_modes[index] = 0
                continue

            mode = self.contact_modes[index]
            if inside or mode == 0:
                mode = self._resolve_contact_mode(point, collider, player_hitbox, self.contact_modes[index])
                self.contact_modes[index] = mode

            if mode == 0:
                if point[0] < player_hitbox.left - self.top_hold_margin:
                    self.contact_modes[index] = -1
                    mode = -1
                elif point[0] > player_hitbox.right + self.top_hold_margin:
                    self.contact_modes[index] = 1
                    mode = 1

            if mode == 0:
                target_x = point[0]
                target_y = player_hitbox.top - self.collision_padding
            elif mode < 0:
                if point[0] < player_hitbox.left - self.contact_release_distance:
                    self.contact_modes[index] = 0
                    continue
                target_x = player_hitbox.left - side_offset
                target_y = point[1]
            elif mode > 0:
                if point[0] > player_hitbox.right + self.contact_release_distance:
                    self.contact_modes[index] = 0
                    continue
                target_x = player_hitbox.right + side_offset
                target_y = point[1]
            else:
                self.contact_modes[index] = 0
                continue

            target_x += self.collider_velocity[0]
            point[0] += (target_x - point[0]) * self.contact_blend
            point[1] += (target_y - point[1]) * self.contact_blend

            # Damp local oscillation while keeping the contact state stable.
            self.prev_points[index][0] = point[0] - self.collider_velocity[0] * 0.25
            self.prev_points[index][1] = point[1]

    def _track_collider(self, entity):
        if not hasattr(entity, 'hitbox'):
            return

        pad_x = self.body_width + self.collision_padding * 2
        pad_y = self.collision_padding * 2
        self.player_hitbox = entity.hitbox.copy()
        self.collider = entity.hitbox.inflate(pad_x, pad_y)
        if self.prev_collider is None:
            self.collider_velocity[0] = 0.0
            self.collider_velocity[1] = 0.0
        else:
            self.collider_velocity[0] = self.collider.centerx - self.prev_collider.centerx
            self.collider_velocity[1] = self.collider.centery - self.prev_collider.centery
        self.prev_collider = self.collider.copy()

    def collision(self, entity):
        self.is_colliding = True
        self._track_collider(entity)

    def on_collision(self, entity):
        pass

    def take_dmg(self, damage):
        pass

    def on_noncollision(self, entity):
        self.is_colliding = False
        self.collider = None
        self.player_hitbox = None
        self.prev_collider = None
        self.collider_velocity[0] = 0.0
        self.collider_velocity[1] = 0.0
        for index in range(1, self.point_count):
            self.contact_modes[index] = 0

    def update(self, dt):
        self.time += dt
        self._integrate(dt)
        iterations = self.active_constraint_iterations if self.is_colliding else self.idle_constraint_iterations
        for _ in range(iterations):
            self._solve_constraints()
            if self.is_colliding:
                self._solve_body_collision()

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