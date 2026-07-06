def parse_pair(value):
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return [int(value[0]), int(value[1])]
    raise KeyError("Boss encounter coordinates must be formatted as [x, y]")


def _resolve_anchor_position(actor, anchor):
    rect = getattr(actor, "hitbox", None) or getattr(actor, "rect", None)
    if rect is None:
        raise KeyError(f"Actor '{actor}' does not expose rect or hitbox for encounter positioning")

    if anchor == "topleft":
        return [rect.left, rect.top]
    if anchor == "midbottom":
        return [rect.midbottom[0], rect.midbottom[1]]
    return [rect.centerx, rect.centery]


def resolve_position(position_config, actors):
    if "spawn_position" in position_config:
        return parse_pair(position_config["spawn_position"])

    relative_to = position_config.get("relative_to")
    if relative_to is None:
        raise KeyError("Boss encounter position requires 'spawn_position' or 'relative_to'")

    actor = actors.get(relative_to)
    if actor is None:
        raise KeyError(f"Boss encounter could not resolve actor '{relative_to}' for relative positioning")

    offset = parse_pair(position_config.get("offset", [0, 0]))
    anchor_position = _resolve_anchor_position(actor, position_config.get("anchor", "center"))
    return [anchor_position[0] + offset[0], anchor_position[1] + offset[1]]


def _resolve_existing_boss(game_objects, encounter_id, boss_config):
    boss_id = boss_config.get("id", encounter_id)
    boss = game_objects.map.ctx.references.get(boss_id)
    if boss is None:
        raise KeyError(f"Boss encounter '{encounter_id}' could not resolve existing boss '{boss_id}'")
    return boss


def _spawn_boss(game_objects, encounter_id, boss_config, actors):
    boss_name = boss_config["class"]
    boss_cls = game_objects.registry.fetch("enemies", boss_name)
    if boss_cls is None:
        raise KeyError(f"Unknown boss enemy: {boss_name}")

    boss_id = boss_config.get("id", encounter_id)
    spawn_position = resolve_position(boss_config, actors)
    initial_state = boss_config.get("initial_state")

    spawn_kwargs = {"ID": boss_id}
    if initial_state is not None:
        spawn_kwargs["initial_state"] = initial_state

    boss = boss_cls(spawn_position, game_objects, **spawn_kwargs)
    game_objects.enemies.add(boss)
    game_objects.map.ctx.references[boss_id] = boss
    return boss


def resolve_boss_for_encounter(game_objects, encounter_id, config, actors):
    boss_config = config["boss"]
    mode = boss_config["mode"]

    if mode == "existing":
        return _resolve_existing_boss(game_objects, encounter_id, boss_config)
    if mode == "spawned":
        return _spawn_boss(game_objects, encounter_id, boss_config, actors)

    raise KeyError(f"Unknown boss encounter mode: {mode}")
