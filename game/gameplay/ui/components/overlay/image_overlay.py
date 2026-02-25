from .base_overlay import BaseOverlay

class ImageOverlay(BaseOverlay):
    def __init__(
        self,
        game_objects,
        texture,
        *,
        pos=(0, 0),
        fade_in=0.25,
        hold=1.2,
        fade_out=0.35,
        channel=None,
        scale=1.0,
    ):
        self.go = game_objects
        self.texture = texture
        self.pos = pos
        self.fade_in = float(fade_in)
        self.hold = float(hold)
        self.fade_out = float(fade_out)
        self.t = 0.0
        self.done = False
        self.channel = channel
        self.scale = float(scale)
        self._lifetime = self.fade_in + self.hold + self.fade_out

    def update(self, dt):
        self.t += float(dt)
        if self.t >= self._lifetime:
            self.done = True

    def _alpha(self):
        t = self.t
        if self.fade_in > 0 and t < self.fade_in:
            a = t / self.fade_in
        elif t < self.fade_in + self.hold:
            a = 1.0
        else:
            out_t = t - (self.fade_in + self.hold)
            a = 1.0 - (out_t / self.fade_out if self.fade_out > 0 else 1.0)
        return max(0.0, min(1.0, a))

    def draw(self, target):
        a = self._alpha()
        # assuming your display.render supports color/alpha; if not, you’ll need a tinted shader variant
        self.go.game.display.render(self.texture, target, position=self.pos, scale=self.scale, alpha=a)