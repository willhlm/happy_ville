def normalize_rgba255(colour):
    values = list(colour or [255, 255, 255, 255])
    if len(values) == 3:
        values.append(255)
    return [channel / 255 for channel in values[:4]]


def resolve_center_getter(target):
    if hasattr(target, "hitbox"):
        return lambda: target.hitbox.center
    if hasattr(target, "rect"):
        return lambda: target.rect.center
    if hasattr(target, "position"):
        return lambda: target.position
    raise AttributeError(f"Light target {target!r} has no hitbox, rect, or position")


def iter_behaviour_specs(behaviours):
    if not behaviours:
        return

    if isinstance(behaviours, dict):
        for name, cfg in behaviours.items():
            yield name, dict(cfg or {})
        return

    for spec in behaviours:
        if isinstance(spec, str):
            yield spec, {}
            continue

        if not isinstance(spec, dict):
            raise TypeError(f"Unsupported light behaviour spec: {spec!r}")

        if "type" in spec:
            cfg = dict(spec)
            name = cfg.pop("type")
            yield name, cfg
            continue

        if len(spec) == 1:
            name, cfg = next(iter(spec.items()))
            yield name, dict(cfg or {})
            continue

        raise ValueError(f"Ambiguous light behaviour spec: {spec!r}")
