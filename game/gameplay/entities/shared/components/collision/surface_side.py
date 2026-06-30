SURFACE_SIDES = ("bottom", "left", "top", "right")

SURFACE_ANGLE_BY_SIDE = {
    "bottom": 0,
    "left": 90,
    "top": 180,
    "right": -90,
}

SURFACE_BODY_ANCHOR_BY_SIDE = {
    "bottom": "midbottom",
    "left": "midleft",
    "top": "midtop",
    "right": "midright",
}


def get_surface_draw_flip(surface_side, tangent):
    if surface_side == "bottom":
        return tangent[0] > 0
    if surface_side == "top":
        return tangent[0] < 0
    if surface_side == "left":
        return tangent[1] > 0
    if surface_side == "right":
        return tangent[1] < 0

    raise ValueError(f"Unsupported surface side: {surface_side}")
