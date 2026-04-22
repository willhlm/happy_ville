class MotionContext:
    __slots__ = ("entity", "requested_motion", "remaining_motion")

    def __init__(self, entity, requested_motion, remaining_motion):
        self.entity = entity
        self.requested_motion = requested_motion
        self.remaining_motion = remaining_motion

    entity: object
    requested_motion: list
    remaining_motion: list


class PlatformCollisionSolver:
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def solve(self, entity, dt):
        if not self._is_collidable(entity):
            return

        entity_dt = entity.hitstop.get_sim_dt(dt)
        support_motion = self._begin_step(entity, entity_dt)
        motion = MotionContext(
            entity=entity,
            requested_motion=[
                entity.velocity[0] * entity_dt + support_motion[0],
                entity.velocity[1] * entity_dt + support_motion[1],
            ],
            remaining_motion=[
                entity.velocity[0] * entity_dt + support_motion[0],
                entity.velocity[1] * entity_dt + support_motion[1],
            ],
        )

        if self._resolve_motion(motion):
            self._update_drop_through_state(entity)
            self._finalize_step(entity)
            return

        self._resolve_passive_platform_overlaps(entity)
        self._update_drop_through_state(entity)
        self._finalize_step(entity)

    def _is_collidable(self, entity):
        platform_collider = getattr(entity, "platform_collider", None)
        if platform_collider:
            return platform_collider.can_collide()
        return True

    def _begin_step(self, entity, entity_dt):
        entity.old_hitbox = entity.hitbox.copy()
        contact_state = getattr(entity, 'contact_state', None)
        support_motion = [0.0, 0.0]
        if contact_state:
            contact_state.begin_step((0.0, 0.0), entity.old_hitbox)

            support_body = contact_state.previous_support_body
            if support_body:
                raw_support_motion = getattr(support_body, 'get_support_motion', lambda _entity: None)(entity)
                if raw_support_motion is not None:
                    if entity.should_apply_support_motion('x', raw_support_motion[0]):
                        support_motion[0] = raw_support_motion[0]
                    if entity.should_apply_support_motion('y', raw_support_motion[1]):
                        support_motion[1] = raw_support_motion[1]

            contact_state.motion_result.requested_motion = (
                entity.velocity[0] * entity_dt + support_motion[0],
                entity.velocity[1] * entity_dt + support_motion[1],
            )
            contact_state.applied_support_motion = (support_motion[0], support_motion[1])

        return support_motion

    def _finalize_step(self, entity):
        contact_state = getattr(entity, 'contact_state', None)
        if not contact_state:
            return

        contact_state.finalize()
        contact_state.complete_motion(entity.hitbox)

    def _resolve_motion(self, motion):
        for _ in range(4):
            axis = self._choose_motion_axis(motion.remaining_motion)
            if axis is None:
                break

            if self._move_and_collide_axis(motion, axis):
                return True

        return False

    def _choose_motion_axis(self, remaining_motion):
        abs_x = abs(remaining_motion[0])
        abs_y = abs(remaining_motion[1])

        if abs_x == 0 and abs_y == 0:
            return None
        if abs_y > abs_x:
            return 'y'
        return 'x'

    def _move_and_collide_axis(self, motion, axis):
        entity = motion.entity
        amount = motion.remaining_motion[0] if axis == 'x' else motion.remaining_motion[1]
        if amount == 0:
            return False

        collision_count_before = self._get_collision_count(entity)
        start_axis_pos = self._get_axis_position(entity, axis)

        if axis == 'x':
            entity.body.move_x(amount)
        else:
            entity.body.move_y(amount)

        overlapping = self._gather_platform_colliders(entity)
        if amount != 0 and self._handle_crush(entity, overlapping, axis=axis):
            return True

        if axis == 'x':
            self._resolve_horizontal_contacts(entity, overlapping, motion)
        elif amount >= 0:
            self._resolve_floor_contacts(entity, overlapping, motion)
        else:
            self._resolve_ceiling_contacts(entity, overlapping, motion)

        end_axis_pos = self._get_axis_position(entity, axis)
        actual_travel = end_axis_pos - start_axis_pos
        axis_index = 0 if axis == 'x' else 1
        blocked_remainder = amount - actual_travel
        motion.remaining_motion[axis_index] = 0

        if blocked_remainder != 0 and self._get_collision_count(entity) > collision_count_before:
            self._clip_remaining_motion(entity, motion.remaining_motion, axis)

        return False

    def _resolve_floor_contacts(self, entity, colliders, motion):
        old_hitbox = getattr(entity, 'old_hitbox', entity.hitbox)
        current_hitbox = entity.hitbox
        if motion.requested_motion[1] < 0:
            return None

        max_step_up = abs(motion.requested_motion[0]) + max(0, motion.requested_motion[1]) + 2
        best_sample = None
        candidate_descriptions = []

        for platform in colliders:
            for sample in platform.get_floor_samples(entity):
                acceptor = sample.source
                if not acceptor.accepts_floor_contact(entity, old_hitbox, current_hitbox, sample.position, max_step_up):
                    continue
                candidate_descriptions.append(
                    f"{type(platform).__name__}:{sample.side}@{sample.position:.3f}:{sample.collision_kind}"
                )
                if best_sample is None or sample.position < best_sample.position:
                    best_sample = sample

        if best_sample is None:
            return None

        entity.platform_collider.push_vertical_sample(best_sample)
        if best_sample.clamp_floor:
            entity.platform_collider.clamp_vertical_velocity()
        self._notify_collision_sample(entity, best_sample, axis='y')
        return best_sample.collider

    def _resolve_ceiling_contacts(self, entity, colliders, motion):
        old_hitbox = getattr(entity, 'old_hitbox', entity.hitbox)
        current_hitbox = entity.hitbox
        max_step_down = abs(motion.requested_motion[0]) + abs(min(0, motion.requested_motion[1])) + 2
        best_sample = None
        candidate_descriptions = []

        for platform in colliders:
            for sample in platform.get_ceiling_samples(entity):
                acceptor = sample.source
                if not acceptor.accepts_ceiling_contact(entity, old_hitbox, current_hitbox, sample.position, max_step_down):
                    continue
                candidate_descriptions.append(
                    f"{type(platform).__name__}:{sample.side}@{sample.position:.3f}:{sample.collision_kind}"
                )
                if best_sample is None or sample.position > best_sample.position:
                    best_sample = sample

        if best_sample is None:
            return None

        entity.platform_collider.push_vertical_sample(best_sample)
        self._notify_collision_sample(entity, best_sample, axis='y')
        return best_sample.collider

    def _resolve_wall_contacts(self, entity, colliders, motion, ignored_collider=None):
        old_hitbox = getattr(entity, 'old_hitbox', entity.hitbox)
        current_hitbox = entity.hitbox
        moving_right = motion.requested_motion[0] > 0
        moving_left = motion.requested_motion[0] < 0
        best_sample = None
        candidate_descriptions = []

        for platform in colliders:
            if platform is ignored_collider:
                continue

            for sample in platform.get_wall_samples(entity):
                if sample.side == 'right' and moving_right:
                    if current_hitbox.right >= sample.position and old_hitbox.right <= sample.position + 1:
                        candidate_descriptions.append(
                            f"{type(platform).__name__}:{sample.side}@{sample.position:.3f}:{sample.collision_kind}"
                        )
                        if best_sample is None or sample.position < best_sample.position:
                            best_sample = sample
                elif sample.side == 'left' and moving_left:
                    if current_hitbox.left <= sample.position and old_hitbox.left >= sample.position - 1:
                        candidate_descriptions.append(
                            f"{type(platform).__name__}:{sample.side}@{sample.position:.3f}:{sample.collision_kind}"
                        )
                        if best_sample is None or sample.position > best_sample.position:
                            best_sample = sample

        if best_sample is None:
            return None

        entity.platform_collider.push_horizontal_sample(best_sample)
        self._notify_collision_sample(entity, best_sample, axis='x')
        return best_sample.collider

    def _notify_collision_sample(self, entity, sample, axis):
        sample.collider.on_platform_collision(entity, sample.side, axis, sample.collision_kind)
        if sample.source is not sample.collider:
            sample.source.on_platform_collision(entity, sample.side, axis, sample.collision_kind)

    def _resolve_horizontal_contacts(self, entity, colliders, motion):
        support_collider = None
        if self._should_resolve_floor_on_horizontal(entity, motion):
            support_collider = self._resolve_floor_contacts(entity, colliders, motion)
        if support_collider is not None:
            colliders = self._refresh_colliders(entity, axis='x', phase='floor')

        wall_collider = self._resolve_wall_contacts(entity, colliders, motion, ignored_collider=support_collider)
        if wall_collider is not None:
            return

        self._resolve_ceiling_contacts(entity, colliders, motion)

    def _refresh_colliders(self, entity, axis, phase):
        return self._gather_platform_colliders(entity)

    def _should_resolve_floor_on_horizontal(self, entity, motion):
        contact_state = getattr(entity, 'contact_state', None)
        if contact_state is None:
            return True

        if contact_state.was_on_wall and motion.requested_motion[1] > 0:
            return False

        return True

    def _clip_remaining_motion(self, entity, remaining_motion, axis):
        collision = self._get_latest_axis_collision(entity, axis)
        if collision is None:
            return

        nx, ny = collision.normal
        dot = remaining_motion[0] * nx + remaining_motion[1] * ny
        if dot >= 0:
            return

        remaining_motion[0] -= dot * nx
        remaining_motion[1] -= dot * ny

    def _get_latest_axis_collision(self, entity, axis):
        contact_state = getattr(entity, 'contact_state', None)
        if not contact_state:
            return None

        for collision in reversed(contact_state.collisions):
            if collision.axis == axis:
                return collision
        return None

    def _get_collision_count(self, entity):
        contact_state = getattr(entity, 'contact_state', None)
        if not contact_state:
            return 0
        return contact_state.get_slide_collision_count()

    def _get_axis_position(self, entity, axis):
        if axis == 'x':
            return entity.hitbox.left
        return entity.hitbox.top

    def _gather_platform_colliders(self, entity):
        colliders = list(self.game_objects.physics.platform_spatial_index.query_rect(entity.hitbox))
        support_candidates = self._get_support_touch_candidates(entity)
        if not support_candidates:
            return colliders

        seen = {id(platform) for platform in colliders}
        for platform in support_candidates:
            platform_id = id(platform)
            if platform_id in seen:
                continue
            if not self._is_touching_support(entity, platform):
                continue
            colliders.append(platform)
            seen.add(platform_id)
        return colliders

    def _get_support_touch_candidates(self, entity):
        contact_state = getattr(entity, 'contact_state', None)
        if contact_state is None:
            return ()

        candidates = []
        for platform in (
            getattr(contact_state, 'support_body', None),
            getattr(contact_state, 'previous_support_body', None),
        ):
            if platform is not None:
                candidates.append(platform)
        return candidates

    def _is_touching_support(self, entity, platform):
        hitbox = entity.hitbox
        platform_hitbox = getattr(platform, 'hitbox', None)
        if platform_hitbox is None:
            return False

        tolerance = self._get_support_contact_tolerance(entity)
        touching_top = abs(hitbox.bottom - platform_hitbox.top) <= tolerance
        overlap_x = (
            hitbox.right > platform_hitbox.left and
            hitbox.left < platform_hitbox.right
        )
        return touching_top and overlap_x

    @staticmethod
    def _get_support_contact_tolerance(entity):
        getter = getattr(entity, 'get_support_contact_tolerance', None)
        if getter is None:
            return 1
        return getter()

    def _resolve_passive_platform_overlaps(self, entity):
        moving_colliders = [
            platform for platform in self._gather_platform_colliders(entity)
            if getattr(platform, 'delta', [0, 0]) != [0, 0]
        ]
        if not moving_colliders:
            return

        for _ in range(2):
            any_resolved = False
            for platform in moving_colliders:
                any_resolved = self._resolve_passive_overlap(entity, platform) or any_resolved

            if not any_resolved:
                break

    def _resolve_passive_overlap(self, entity, platform, eps=1):
        if not entity.hitbox.colliderect(platform.hitbox):
            return False

        dx, dy = getattr(platform, 'delta', [0, 0])
        if dx == 0 and dy == 0:
            return False

        old_entity_hitbox = getattr(entity, 'old_hitbox', entity.hitbox)
        old_platform_hitbox = getattr(platform, 'old_hitbox', platform.hitbox)
        vertical_side = self._get_passive_vertical_side(old_entity_hitbox, old_platform_hitbox, eps)
        horizontal_side = self._get_passive_horizontal_side(old_entity_hitbox, old_platform_hitbox, eps)

        use_vertical = abs(dy) >= abs(dx) and dy != 0
        if use_vertical:
            if vertical_side is not None:
                side = vertical_side
            elif horizontal_side is not None:
                side = horizontal_side
                use_vertical = False
            else:
                entity.platform_collider.handle_crush(platform)
                return True

        if use_vertical:
            entity.platform_collider.push_vertical(platform, side)
            if side == 'bottom':
                entity.platform_collider.clamp_vertical_velocity()
            platform.on_platform_collision(entity, side, 'y')
            chained = self._would_chain_passive_overlap(entity, platform, side)
            if chained:
                entity.platform_collider.handle_crush(platform, side=side)
            return True

        if horizontal_side is not None:
            side = horizontal_side
        elif vertical_side is not None:
            side = vertical_side
            use_vertical = True
        else:
            entity.platform_collider.handle_crush(platform)
            return True

        if use_vertical:
            entity.platform_collider.push_vertical(platform, side)
            if side == 'bottom':
                entity.platform_collider.clamp_vertical_velocity()
            platform.on_platform_collision(entity, side, 'y')
            chained = self._would_chain_passive_overlap(entity, platform, side)
            if chained:
                entity.platform_collider.handle_crush(platform, side=side)
            return True

        entity.platform_collider.push_horizontal(platform, side)
        platform.on_platform_collision(entity, side, 'x')
        chained = self._would_chain_passive_overlap(entity, platform, side)
        if chained:
            entity.platform_collider.handle_crush(platform, side=side)
        return True

    @staticmethod
    def _get_passive_vertical_side(old_entity_hitbox, old_platform_hitbox, eps):
        if old_entity_hitbox.bottom <= old_platform_hitbox.top + eps:
            return 'bottom'
        if old_entity_hitbox.top >= old_platform_hitbox.bottom - eps:
            return 'top'
        return None

    @staticmethod
    def _get_passive_horizontal_side(old_entity_hitbox, old_platform_hitbox, eps):
        if old_entity_hitbox.right <= old_platform_hitbox.left + eps:
            return 'right'
        if old_entity_hitbox.left >= old_platform_hitbox.right - eps:
            return 'left'
        return None

    def _would_chain_passive_overlap(self, entity, platform, side):
        if entity.hitbox.colliderect(platform.hitbox):
            return True

        projected = entity.hitbox.copy()
        return entity.platform_collider.crush_resolver.has_opposite_blocker(platform, side, projected=projected)

    def _handle_crush(self, entity, colliders, axis):
        if len(colliders) < 2:
            return False

        if not any(getattr(platform, 'delta', [0, 0]) != [0, 0] for platform in colliders):
            return False

        for platform in colliders:
            if not hasattr(platform, 'delta'):
                continue

            dx, dy = platform.delta
            if dx == 0 and dy == 0:
                continue

            if dy > 0:
                crushed = entity.platform_collider.is_crushed(platform, 'top')
                if crushed:
                    entity.platform_collider.handle_crush(platform, side='top')
                    return True
            if dy < 0:
                crushed = entity.platform_collider.is_crushed(platform, 'bottom')
                if crushed:
                    entity.platform_collider.handle_crush(platform, side='bottom')
                    return True
            if dx > 0:
                crushed = entity.platform_collider.is_crushed(platform, 'left')
                if crushed:
                    entity.platform_collider.handle_crush(platform, side='left')
                    return True
            if dx < 0:
                crushed = entity.platform_collider.is_crushed(platform, 'right')
                if crushed:
                    entity.platform_collider.handle_crush(platform, side='right')
                    return True

        return False

    def _update_drop_through_state(self, entity):
        go_through = getattr(entity, 'go_through', None)
        if not go_through or 'drop_through' not in go_through:
            return
        if not go_through['drop_through']:
            return

        probe = entity.hitbox.copy()
        probe.bottom += 1
        platforms = self.game_objects.physics.platform_spatial_index.query_rect(probe)

        for platform in platforms:
            if platform.supports_drop_through(entity, probe) is not None:
                return

        go_through['drop_through'] = False
