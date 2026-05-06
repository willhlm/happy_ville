from weakref import WeakSet

from . import effects


class LayerResourcePool:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._layer_cache = {}
        self._pipelines = WeakSet()

    def register_pipeline(self, pipeline):
        self._pipelines.add(pipeline)

    def acquire_layers(self, size):
        return self.acquire_named_layers("pipeline", size, 3)

    def acquire_named_layers(self, cache_key, size, count):
        size = tuple(size)
        cache_entry = (cache_key, size, count)
        cached_layers = self._layer_cache.get(cache_entry)
        if cached_layers is not None:
            return cached_layers

        display = self.game_objects.game.display
        cached_layers = tuple(display.make_layer(size) for _ in range(count))
        self._layer_cache[cache_entry] = cached_layers
        return cached_layers

    def flush(self):
        for pipeline in list(self._pipelines):
            pipeline.invalidate_resources()

        for layers in self._layer_cache.values():
            for layer in layers:
                layer.release()
        self._layer_cache.clear()

        for effect_name in getattr(effects, "__all__", []):
            effect_class = getattr(effects, effect_name, None)
            if effect_class is None:
                continue
            effect_class.flush_cache()
