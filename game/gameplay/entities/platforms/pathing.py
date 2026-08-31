"""Shared coordinate conventions for platforms that follow Tiled paths."""


def centre_path_to_topleft(points, size):
    """Convert centre-authored Tiled path points to platform top-left points."""
    width, height = size
    return [(x - width / 2, y - height / 2) for x, y in points]
