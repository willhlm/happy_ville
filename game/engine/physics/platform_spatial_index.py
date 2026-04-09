class PlatformSpatialIndex:
    DEFAULT_CELL_SIZE = 64

    def __init__(self, cell_size=DEFAULT_CELL_SIZE):
        self.cell_size = max(1, int(cell_size))
        self._cells = {}

    def clear(self):
        self._cells.clear()

    def rebuild(self, platforms):
        self.clear()
        for platform in platforms:
            hitbox = getattr(platform, 'hitbox', None)
            if hitbox is None or hitbox.width < 0 or hitbox.height < 0:
                continue

            for cell in self._iter_hitbox_cells(hitbox):
                bucket = self._cells.setdefault(cell, [])
                bucket.append(platform)

    def query_rect(self, rect):
        matches = []
        seen = set()

        for cell in self._iter_hitbox_cells(rect):
            for platform in self._cells.get(cell, ()):
                platform_id = id(platform)
                if platform_id in seen:
                    continue
                seen.add(platform_id)
                if rect.colliderect(platform.hitbox):
                    matches.append(platform)

        return matches

    def query_point(self, point):
        cell = self._point_to_cell(point)
        for platform in self._cells.get(cell, ()):
            if platform.hitbox.collidepoint(point):
                return platform
        return None

    def _iter_hitbox_cells(self, hitbox):
        left = hitbox.left // self.cell_size
        right = (hitbox.right - 1) // self.cell_size
        top = hitbox.top // self.cell_size
        bottom = (hitbox.bottom - 1) // self.cell_size

        for cell_x in range(left, right + 1):
            for cell_y in range(top, bottom + 1):
                yield (cell_x, cell_y)

    def _point_to_cell(self, point):
        return (point[0] // self.cell_size, point[1] // self.cell_size)

