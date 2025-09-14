import pygame
from gameplay.entities.platforms.base.platform import Platform

class CollisionPolygon(Platform):
    def __init__(self, pos, points, go_through=True):
        super().__init__(pos, size=(0, 0))
        self.go_through = go_through
        self.points = [[p[0] + pos[0], p[1] + pos[1]] for p in points]

        xs, ys = zip(*self.points)
        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)
        self.hitbox = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


        #cut_start = (400, 320)
        #cut_end = (480, 464)

        #for ramp in self.entity.game_objects.platforms_ramps.sprites():
        #    new_pieces = ramp.cut(cut_start, cut_end)
        #    ramp.kill()

        # Replace original with new ones in your world
        #for piece in new_pieces:
        #    if type(piece).__name__ == 'Collision_right_angle':
        #        self.entity.game_objects.platforms_ramps.add(piece)
        #    else:
        #        self.entity.game_objects.platforms.add(piece)


    def collide(self, entity):
        result = self.polygon_collision(self.points, entity.hitbox)
        if result is None:
            return  # No collision

        overlap, axis = result
        # Move entity out of the polygon
        direction = (entity.hitbox.centerx - self.rect.centerx, entity.hitbox.centery - self.rect.centery)
        sign = 1 if self.dot(direction, axis) > 0 else -1
        move_x = axis[0] * overlap * sign
        move_y = axis[1] * overlap * sign

        entity.hitbox.x += move_x
        entity.hitbox.y += move_y
        entity.update_rect_x()
        entity.update_rect_y()

    def dot(self, a, b):
        return a[0]*b[0] + a[1]*b[1]

    def project_polygon(self, axis, points):
        dots = [self.dot(p, axis) for p in points]
        return min(dots), max(dots)

    def normalize(self, v):
        length = math.hypot(v[0], v[1])
        if length == 0:
            return (0, 0)
        return (v[0]/length, v[1]/length)

    def get_axes(self, polygon):
        axes = []
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])
            axes.append(self.normalize(normal))
        return axes

    def polygon_collision(self, poly, rect):
        rect_points = [
            rect.topleft,
            rect.topright,
            rect.bottomright,
            rect.bottomleft
        ]

        axes = self.get_axes(poly) + [(1,0), (0,1)]  # rect is axis-aligned

        min_overlap = float('inf')
        mtv_axis = None

        for axis in axes:
            proj1 = self.project_polygon(axis, poly)
            proj2 = self.project_polygon(axis, rect_points)

            overlap = min(proj1[1], proj2[1]) - max(proj1[0], proj2[0])
            if overlap <= 0:
                return None  # No collision
            if overlap < min_overlap:
                min_overlap = overlap
                mtv_axis = axis

        return (min_overlap, mtv_axis)
