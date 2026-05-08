def resolve_distance(entity, cfg, default_key):
    distance_key = cfg.get('distance', default_key)
    return entity.config['distances'][distance_key]
