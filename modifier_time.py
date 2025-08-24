import sys

class TimeManager():
    def __init__(self, entity):
        self.entity = entity
        self.modifiers = {}
        self._sorted_modifiers = []        

    def add_modifier(self, modifier, priority = 0, **kwarg):
        new_modifier = getattr(sys.modules[__name__], modifier)(priority, **kwarg)
        self.modifiers[modifier] = new_modifier
        self._sort_modifiers()

    def remove_modifier(self, modifier):
        del self.modifiers[modifier]
        self._sort_modifiers()

    def clear_modifiers(self):
        self.modifiers.clear()
        self._sorted_modifiers.clear()

    def _sort_modifiers(self):
        self._sorted_modifiers = sorted(self.modifiers.values(), key = lambda m: m.priority, reverse = True)        

    def resolve(self, dt):
        context = TimeContext(dt)
        for mod in self._sorted_modifiers:
            mod.apply(context)
        return context

class TimeContext():
    def __init__(self, dt):
        self.dt = dt                

class HitStop():
    def __init__(self, priority, **kwargs):
        self.entity = kwargs['entity']
        self.priority = priority
        self.lifetime = kwargs.get('lifetime', 0.1)
        self.scale = kwargs.get('scale', 1.0)
        self.call_back = kwargs.get('call_back', None)

    def apply(self, context):
        self.lifetime -= context.dt
        context.dt *= self.scale
        if self.lifetime <= 0:
            self.entity.time_manager.remove_modifier('HitStop')
            if self.call_back: self.call_back()
                
