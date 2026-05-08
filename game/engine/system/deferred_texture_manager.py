class DeferredTextureManager:
    def __init__(self):
        self._entities = []
        self._entity_ids = set()

    def track(self, entity):
        entity_id = id(entity)
        if entity_id in self._entity_ids:
            return

        self._entities.append(entity)
        self._entity_ids.add(entity_id)

    def release_all(self):
        for entity in self._entities:
            entity.release_texture()

        self._entities.clear()
        self._entity_ids.clear()
