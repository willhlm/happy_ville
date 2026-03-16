from gameplay.ui.components.overlay.point_arrow import PointArrow


class HudWidgets:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.widgets = {}

    def update(self, dt):
        for widget in self.widgets.values():
            widget.update(dt)

    def draw(self, target):
        for widget in self.widgets.values():
            widget.draw(target)

    def show_point_arrow(self, key, pos, dir):
        arrow = PointArrow(self.game_objects, pos=pos, dir=dir)
        self.widgets[key] = arrow
        return arrow

    def hide(self, key):
        self.widgets.pop(key, None)
