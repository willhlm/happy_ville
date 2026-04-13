import math


def resolve_tileset(map_def, gid: int):
    chosen = None
    for firstgid, source in map_def.tileset_ranges:
        if firstgid <= gid:
            chosen = (firstgid, source)
        else:
            break
    if chosen is None:
        return None, None, None
    firstgid, source = chosen
    local_id = gid - firstgid
    return source, firstgid, local_id


def props_list_to_dict(properties):
    return {p["name"]: p.get("value") for p in (properties or [])}


def calculate_object_position(obj, parallax, offset, viewport_center):
    new_map_diff = [-viewport_center[0], -viewport_center[1]]
    object_size = [int(obj["width"]), int(obj["height"])]
    object_position = [
        int(obj["x"]) - math.ceil((1 - parallax[0]) * new_map_diff[0]) + offset[0],
        int(obj["y"]) - math.ceil((1 - parallax[1]) * new_map_diff[1]) + offset[1] - object_size[1],
    ]
    return object_position, object_size
