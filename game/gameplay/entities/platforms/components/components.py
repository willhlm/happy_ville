import math, pygame
from .states_time_collision import Idle
from gameplay.entities.shared.components import hit_effects
# ----------------------------
# Component base
# ----------------------------

class PlatformComponent:
    """
    Hooks are optional. Component can implement any of:
      - on_added(platform)
      - update(dt)
      - collide_x(entity)
      - collide_y(entity)
      - take_dmg(projectile)
      - lever_hit() / signal_hit() etc (custom)
    """
    def __init__(self, platform, **props):
        self.p = platform
        self.props = props

    def on_added(self):
        pass

    def update(self, dt):
        pass

    def collide_x(self, entity):
        pass

    def collide_y(self, entity):
        pass

    def take_dmg(self, projectile):
        pass

# ----------------------------
# Collision components
# ----------------------------

class SolidCollision(PlatformComponent):
    def collide_x(self, entity):
        eps = 1

        hit_from_left = (
            entity.hitbox.right >= self.p.hitbox.left and
            entity.old_hitbox.right <= self.p.old_hitbox.left + eps
        )
        hit_from_right = (
            entity.hitbox.left <= self.p.hitbox.right and
            entity.old_hitbox.left >= self.p.old_hitbox.right - eps
        )

        if hit_from_left:
            entity.right_collision(self.p)
        elif hit_from_right:
            entity.left_collision(self.p)

        entity.update_rect_x()

    def collide_y(self, entity):
        eps = 1

        landed_from_above = (
            entity.hitbox.bottom >= self.p.hitbox.top and
            entity.old_hitbox.bottom <= self.p.old_hitbox.top + eps
        )
        hit_from_below = (
            entity.hitbox.top <= self.p.hitbox.bottom and
            entity.old_hitbox.top >= self.p.old_hitbox.bottom - eps
        )

        if landed_from_above:
            entity.down_collision(self.p)
            entity.limit_y()
        elif hit_from_below:
            entity.top_collision(self.p)

        entity.update_rect_y()

class CarryOnTop(PlatformComponent):
    def collide_y(self, entity):
        # landing or standing (add eps if needed)
        eps = 2
        on_top_now = abs(entity.hitbox.bottom - self.p.hitbox.top) <= eps
        was_on_top = abs(entity.old_hitbox.bottom - self.p.old_hitbox.top) <= eps

        if on_top_now and was_on_top:
            entity.true_pos[0] += self.p.delta[0]
            entity.true_pos[1] += self.p.delta[1]
            entity.rect.left = round(entity.true_pos[0])
            entity.rect.top  = round(entity.true_pos[1])
            entity.update_hitbox()

class OneWayUpCollision(PlatformComponent):
    """CollisionOnewayUp behavior :contentReference[oaicite:6]{index=6}"""
    def collide_x(self, entity):
        return

    def collide_y(self, entity):
        if entity.velocity[1] < 0:
            return  # going up: ignore
        offset = entity.velocity[1] + abs(entity.velocity[0]) + 1
        if entity.hitbox.bottom <= self.p.hitbox.top + offset:
            entity.down_collision(self.p)
            entity.limit_y()
            entity.update_rect_y()

#notr used
class DamageCollision(PlatformComponent):
    """CollisionDamage-like behavior :contentReference[oaicite:7]{index=7}
       If you only want damage on landing, use DamageOnLand instead.
    """
    def on_added(self):
        dmg = float(self.props.get("dmg", 1))
        self.effect = hit_effects.HitEffect(damage=dmg)

        # knockback defaults (can be overridden)
        self.kx = float(self.props.get("knockback_x", 10))
        self.ky = float(self.props.get("knockback_y", 10))

    def _apply_damage(self, entity, vx, vy):
        effect = self.effect.copy()
        effect.attacker = self.p
        entity.take_hit(effect)
        entity.velocity[0] = vx
        entity.velocity[1] = vy

    def collide_x(self, entity):
        if entity.velocity[0] > 0:
            entity.right_collision(self.p)
            self._apply_damage(entity, -self.kx, entity.velocity[1])
        else:
            entity.left_collision(self.p)
            self._apply_damage(entity, +self.kx, entity.velocity[1])
        entity.update_rect_x()

    def collide_y(self, entity):
        if entity.velocity[1] > 0:
            entity.down_collision(self.p)
            self._apply_damage(entity, entity.velocity[0], -self.ky)
        else:
            entity.top_collision(self.p)
            self._apply_damage(entity, entity.velocity[0], +self.ky)
        entity.update_rect_y()

class DamageOnLand(PlatformComponent):
    """Only hurts when the entity lands from above (common 'spikes-on-top' variant)."""
    def on_added(self):
        dmg = float(self.props.get("dmg", 1))
        self.effect = hit_effects.HitEffect(damage=dmg)
        self.ky = float(self.props.get("knockback_y", 10))

    def collide_y(self, entity):
        if entity.velocity[1] <= 0:
            return
        # treat as a normal solid landing + damage
        entity.down_collision(self.p)
        entity.limit_y()

        effect = self.effect.copy()
        effect.attacker = self.p
        entity.take_hit(effect)
        entity.velocity[1] = -self.ky

        entity.update_rect_y()


# ----------------------------
# Behavior components
# ----------------------------

class Move(PlatformComponent):#wrapper
    def on_added(self):
        t = str(self.props.get("move_type", "direction_distance")).lower()

        variants = {
            "direction_distance": MoveDirectionDistance,
            'path': MovePath,
        }

        cls = variants.get(t)

        self.impl = cls(self.p, **self.props)
        self.impl.on_added()

    def update(self, dt):
        self.impl.update(dt)

class MovePath(PlatformComponent):
    """
    Move along a polyline path from Tiled.

    Props expected:
      path_points: list[(x,y)] world coords
      speed: float px/s (default 80)

      smooth: bool (default False)
      samples_per_segment: int (default 10)

      pingpong: bool (default True)
      loop: bool (default False)  # ignored if pingpong True
      snap_to_path: bool (default True)
      start_index: int (default 0)

      eps: float (default 1.0) snapping tolerance
    """

    def on_added(self):
        pts = self.props.get("path_points")
        self.points = list(pts) if pts else []

        self.speed = float(self.props.get("speed", 80.0)) * 100
        self.eps = float(self.props.get("eps", 1.0))

        self.pingpong = bool(self.props.get("pingpong", True))
        self.loop = bool(self.props.get("loop", False))
        self.snap_to_path = bool(self.props.get("snap_to_path", True))

        self.smooth = bool(self.props.get("smooth", False))
        self.samples_per_segment = int(self.props.get("samples_per_segment", 10))

        self.dir = 1
        self.i = int(self.props.get("start_index", 0))

        if len(self.points) < 2 or self.speed <= 0:
            self.active = False
            return

        # If looping, enforce closed path for continuity (connect last -> first)
        # This avoids teleporting when wrap happens.
        if self.loop and not self.pingpong:
            self._enforce_closed()

        # Optional smoothing (resample into a denser point list)
        if self.smooth and len(self.points) >= 2 and self.samples_per_segment > 1:
            closed_for_spline = self.loop and not self.pingpong
            self.points = self._catmull_rom_resample(self.points, self.samples_per_segment, closed=closed_for_spline)

            # If loop, ensure last==first after resampling too
            if closed_for_spline:
                self._enforce_closed()

        # Clamp index
        self.i = max(0, min(self.i, len(self.points) - 2))

        # Snap platform onto the path at start
        self.snap_mode = str(self.props.get("snap_mode", "closest")).strip().lower()

        if self.snap_to_path:
            if self.snap_mode == "start":
                sx, sy = self.points[self.i]
                self._set_platform_pos(sx, sy)
            else:
                # closest point on the path (segment projection)
                px, py = self.p.true_pos[0], self.p.true_pos[1]
                sx, sy, seg_i = self._snap_closest(px, py)
                self.i = max(0, min(seg_i, len(self.points) - 2))
                self._set_platform_pos(sx, sy)

            # zero velocity so no kick on the first integrate
            if hasattr(self.p, "velocity"):
                self.p.velocity[0] = 0.0
                self.p.velocity[1] = 0.0


        self.active = True

    def _closest_point_on_segment(self, ax, ay, bx, by, px, py):
        # returns (cx, cy, t) where t in [0,1]
        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay

        vv = vx * vx + vy * vy
        if vv <= 1e-9:
            return ax, ay, 0.0

        t = (wx * vx + wy * vy) / vv
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0

        cx = ax + t * vx
        cy = ay + t * vy
        return cx, cy, t

    def _snap_closest(self, x, y):
        """
        Finds closest point on polyline segments.
        Returns (sx, sy, seg_index) where seg_index is the segment start i (point i -> i+1).
        """
        pts = self.points
        best_d2 = float("inf")
        best = (pts[0][0], pts[0][1], 0)

        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            cx, cy, _t = self._closest_point_on_segment(ax, ay, bx, by, x, y)
            dx = cx - x
            dy = cy - y
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = (cx, cy, i)

        return best  # (sx, sy, i)

    def _set_platform_pos(self, x, y):
        # Works with your DynamicPlatform style (true_pos + rect)
        if hasattr(self.p, "true_pos"):
            self.p.true_pos[0] = float(x)
            self.p.true_pos[1] = float(y)
        if hasattr(self.p, "rect"):
            self.p.rect.topleft = (int(x), int(y))
        if hasattr(self.p, "pos"):
            self.p.pos[0] = float(x)
            self.p.pos[1] = float(y)

    def _enforce_closed(self):
        if len(self.points) < 2:
            return
        x0, y0 = self.points[0]
        x1, y1 = self.points[-1]
        if math.hypot(x1 - x0, y1 - y0) > self.eps:
            self.points.append((x0, y0))

    # --- Catmull–Rom smoothing/resampling ---
    def _catmull_rom_resample(self, points, samples_per_segment, closed=False):
        """
        Returns a densified point list passing through the original control points.
        Closed mode wraps endpoints for smooth looping.
        """
        pts = list(points)
        n = len(pts)
        if n < 2:
            return pts

        def catmull(p0, p1, p2, p3, t):
            # standard Catmull-Rom (tension = 0.5 baked in)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3
            )
            return (x, y)

        out = []

        if closed:
            # wrap indices (assumes last==first is fine; we’ll still wrap safely)
            # build segments for each original point -> next point
            base = pts
            m = len(base)
            for i in range(m - 1):  # if last==first, last segment is handled by i=m-2 -> m-1 (which is first)
                p0 = base[(i - 1) % m]
                p1 = base[i % m]
                p2 = base[(i + 1) % m]
                p3 = base[(i + 2) % m]
                if i == 0:
                    out.append(p1)
                for s in range(1, samples_per_segment + 1):
                    t = s / float(samples_per_segment)
                    out.append(catmull(p0, p1, p2, p3, t))
        else:
            # pad endpoints by duplication
            base = [pts[0]] + pts + [pts[-1]]
            # segments run from base[i] -> base[i+1] corresponding to original pts[i-1] -> pts[i]
            for i in range(1, len(base) - 2):
                p0 = base[i - 1]
                p1 = base[i]
                p2 = base[i + 1]
                p3 = base[i + 2]
                if i == 1:
                    out.append(p1)
                for s in range(1, samples_per_segment + 1):
                    t = s / float(samples_per_segment)
                    out.append(catmull(p0, p1, p2, p3, t))

        return out

    # --- movement core ---
    def _advance_waypoint(self):
        n = len(self.points)
        nxt = self.i + self.dir

        if nxt >= n:
            if self.pingpong:
                self.dir = -1
                self.i = n - 1
            elif self.loop:
                self.i = 0
            else:
                self.i = n - 1

        elif nxt < 0:
            if self.pingpong:
                self.dir = 1
                self.i = 0
            elif self.loop:
                self.i = n - 1
            else:
                self.i = 0
        else:
            self.i = nxt

    def update(self, dt):
        if not self.active:
            return

        if dt <= 0:
            self.p.velocity[0] = 0.0
            self.p.velocity[1] = 0.0
            return

        x0, y0 = self.p.true_pos[0], self.p.true_pos[1]
        x, y = x0, y0

        remaining = self.speed * dt
        n = len(self.points)
        self.i = max(0, min(self.i, n - 1))

        safety = 0
        while remaining > 0 and safety < 64:
            safety += 1

            tgt_i = self.i + self.dir
            if tgt_i < 0 or tgt_i >= n:
                self._advance_waypoint()
                continue

            tx, ty = self.points[tgt_i]
            dx = tx - x
            dy = ty - y
            dist = math.hypot(dx, dy)

            if dist <= self.eps:
                x, y = tx, ty
                self.i = tgt_i
                continue

            if dist <= remaining:
                x, y = tx, ty
                remaining -= dist
                self.i = tgt_i
                continue

            ux = dx / dist
            uy = dy / dist
            x += ux * remaining
            y += uy * remaining
            remaining = 0.0

        self.p.velocity[0] = (x - x0) / dt
        self.p.velocity[1] = (y - y0) / dt

class MoveDirectionDistance(PlatformComponent):
    """
    Sine motion, but expressed as velocity so BaseDynamic moves it.
    Props:
      direction: "left","right","up","down" or [x,y]
      distance: amplitude (pixels)
      speed: cycles per second
    """
    def on_added(self):
        self.distance = float(self.props.get("distance", 64))
        self.speed = float(self.props.get("speed", 0.5))  # cycles/sec

        direction = self.props.get("direction", '1,0')
        string_list = direction.split(',')
        self.dir = [int(num) for num in string_list]

        self.t = float(self.props.get("phase", 0.0))  # optional
        self.omega = 2.0 * math.pi * self.speed       # rad/sec

    def update(self, dt):
        self.t += dt

        # position offset would be: distance * sin(omega*t)
        # so velocity is: distance * omega * cos(omega*t)
        v = self.distance * self.omega * math.cos(self.omega * self.t)

        self.p.velocity[0] = self.dir[0] * v
        self.p.velocity[1] = self.dir[1] * v

class DisappearOnStand(PlatformComponent):
    """
    Disappears after standing on it.
    Self-contained: handles gameplay + visual flags + signal wiring.

    Emits:
      platform.disappear_start
      platform.disappear_end
      platform.respawn
    """
    def on_added(self):
        dt = int(self.props.get("disappear_time", 60))
        rt = int(self.props.get("respawn_time", 120))
        self.disappear_time = dt if dt > 0 else 60
        self.respawn_time = rt if rt > 0 else 120

        self._pending = False

        self.timers = self.p.game_objects.timer_manager

        # ensure this platform has the right state machine
        if self.p.currentstate.__class__.__name__ == "_NullState":
            self.p.currentstate = Idle(self.p)        

    def collide_y(self, entity):
        if self._pending:
            return

        # only land from above
        if entity.velocity[1] < 0:
            return

        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.p.hitbox.top + offset:
            self._pending = True

            # enter warning (collidable)
            self.p.currentstate.handle_input("warning")

            # after delay, start transition_1 (turns collision off)
            self.timers.start_timer(self.disappear_time, self._start_disappear)

            entity.down_collision(self.p)
            entity.limit_y()
            entity.update_rect_y()

    def _start_disappear(self):
        self.p.currentstate.handle_input("dissapear")
        self.timers.start_timer(self.respawn_time, self._start_respawn)

    def _start_respawn(self):
        self.p.currentstate.handle_input("re_appear")
        self._pending = False

class Breakable(PlatformComponent):
    """
    Damage receiver with HP + invincibility + direction-dependent vulnerability.

    Props:
        health: int (default 3)
        invincibility_time: int (default 30)
        break_delay: int (default 0)
        disable_collision_on_break: bool (default True)
        shake_on_hit: bool (default True)

        vulnerable_sides: str (default "all")
            Allowed: "all" or comma-separated: "top,bottom,left,right"
            Meaning = "which side the attack must come FROM to deal damage".
            Example: "bottom" => only damage when hit from below (projectile traveling upward into it).
    """

    def on_added(self):
        self.health = int(self.props.get("health", 3))
        self.inv_time = int(self.props.get("invincibility_time", 30))

        sides = self.props.get("vulnerable_sides", "all")
        if sides == "all":
            self.vuln = {"top", "bottom", "left", "right"}
        else:
            self.vuln = sides

        self.inv = False

        self.timers = self.p.game_objects.timer_manager
        self.camera = self.p.game_objects.camera_manager

    def _inv_off(self):
        self.inv = False

    def _get_hit_side(self, src) -> str | None:
        # Require rects
        a = self.p.hitbox
        b = src.hitbox

        # Compute overlaps
        overlap_left   = b.right - a.left
        overlap_right  = a.right - b.left
        overlap_top    = b.bottom - a.top
        overlap_bottom = a.bottom - b.top

        # If any overlap is negative, no collision (safety)
        if overlap_left < 0 or overlap_right < 0 or overlap_top < 0 or overlap_bottom < 0:
            return None

        overlap_x = min(overlap_left, overlap_right)
        overlap_y = min(overlap_top, overlap_bottom)

        # Decide axis by smallest overlap (corner hits choose the "true" side)
        if overlap_x < overlap_y:
            # Horizontal collision
            # If src is more on the left side of platform, it hit from left (moving right)
            return "left" if b.centerx < a.centerx else "right"
        else:
            # Vertical collision
            return "top" if b.centery < a.centery else "bottom"
                
    def take_dmg(self, source):
        """
        Only applies damage if hit direction is allowed by vulnerable_sides.
        """
        if self.inv: return
            
        hit_side = self._get_hit_side(source)
        if hit_side not in self.vuln: return            

        dmg = getattr(source, "dmg", 1)
        self.health -= int(dmg)

        self.inv = True
        self.timers.start_timer(self.inv_time, self._inv_off)

        self.camera.camera_shake(amplitude=3, duration=10)

        if self.health <= 0:
            self.p.kill()

#not used
class ActiveGate(PlatformComponent):
    """
    Generic: subscribe to a signal and gate platform activity.
    Props:
      id: signal key
      mode: "toggle"|"on"|"off" (default toggle)
      affect: "all"|"movement"|"collision" (default all)
    """
    def on_added(self):
        self.signal_id = self.props.get("id")
        self.mode = str(self.props.get("mode", "toggle")).lower()
        self.affect = str(self.props.get("affect", "all")).lower()
        self.active = True

        self._orig_hitbox = self.p.hitbox.copy()
        self.p.game_objects.signals.subscribe(self.signal_id, self._on_signal)

    def _on_signal(self, payload=None):
        if self.mode == "on":
            self.active = True
        elif self.mode == "off":
            self.active = False
        else:
            self.active = not self.active

        # collision gating
        if self.affect in ("all", "collision"):
            if self.active:
                self.p.hitbox = self._orig_hitbox.copy()
            else:
                self.p.hitbox.size = (0, 0)

        # movement gating (stop immediately)
        if self.affect in ("all", "movement"):
            if hasattr(self.p, "velocity"):
                self.p.velocity[0] = 0.0
                self.p.velocity[1] = 0.0


# ----------------------------
# Component registry
# ----------------------------

COMPONENTS = {
    # collision
    "solid": SolidCollision,
    "oneway_up": OneWayUpCollision,
    "carry_on_top": CarryOnTop,

    # behaviors
    "move": Move,
    "disappear_on_stand": DisappearOnStand,
    "breakable": Breakable,
}

