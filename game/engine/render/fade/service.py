import weakref
from .effects import AlphaFadeEffect, DissolveFadeEffect, MaskFadeEffect
from .masks import FadeMaskCache

class FadeService:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.masks = FadeMaskCache(game_objects)
        self._fade_types = {
            "alpha": AlphaFadeEffect,
            "dissolve": DissolveFadeEffect,
            "mask": MaskFadeEffect,
        }
        self._instances = weakref.WeakSet()

    def create(self, style, value=0.0, **kwargs):
        fade_type = self._fade_types[style]
        effect = fade_type(self, value, **kwargs)
        self._instances.add(effect)
        return effect

    def release(self, effect):
        if effect is None:
            return
        effect.release()
        self._instances.discard(effect)

    def release_all(self):
        for effect in list(self._instances):
            effect.release()
        self._instances.clear()
        self.masks.release()
