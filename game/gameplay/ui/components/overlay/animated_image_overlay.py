from engine.utils import read_files

from .base_overlay import BaseOverlay


class AnimatedImageOverlay(BaseOverlay):
    def __init__(
        self,
        game_objects,
        frames,
        *,
        pos=(0, 0),
        fade_in=0.15,
        hold=1.0,
        fade_out=0.25,
        delay=0.0,
        channel=None,
        scale=1.0,
        frame_time=0.1,
        anchor="center",
    ):
        self.go = game_objects
        self.frames = list(frames)
        if not self.frames:
            raise ValueError("AnimatedImageOverlay requires at least one frame.")

        self.pos = pos
        self.fade_in = float(fade_in)
        self.hold = float(hold)
        self.fade_out = float(fade_out)
        self.delay = float(delay)
        self.channel = channel
        self.scale = float(scale)
        self.frame_time = max(float(frame_time), 0.001)
        self.anchor = anchor

        self.t = 0.0
        self.done = False
        self._lifetime = max(0.0, self.fade_in + self.hold + self.fade_out)

    def on_start(self) -> None:
        pass

    def update(self, dt: float) -> None:
        self.t += float(dt)
        if self.t >= self.delay + self._lifetime:
            self.done = True

    def _local_t(self) -> float:
        return max(0.0, self.t - self.delay)

    def _alpha(self) -> float:
        if self.t < self.delay:
            return 0.0

        t = self._local_t()
        if self.fade_in > 0 and t < self.fade_in:
            alpha = t / self.fade_in
        elif t < self.fade_in + self.hold:
            alpha = 1.0
        else:
            out_t = t - (self.fade_in + self.hold)
            alpha = 1.0 - (out_t / self.fade_out if self.fade_out > 0 else 1.0)

        return max(0.0, min(1.0, alpha)) * 255

    def _frame(self):
        frame_index = int(self._local_t() / self.frame_time) % len(self.frames)
        return self.frames[frame_index]

    def _draw_position(self, frame):
        x, y = self.pos
        if self.anchor == "center":
            return (x - frame.width * 0.5, y - frame.height * 0.5)
        if self.anchor == "bottom_right":
            return (x - frame.width, y - frame.height)
        return self.pos

    def draw(self, target):
        if self.t < self.delay:
            return

        self.go.shaders['alpha']['alpha'] = self._alpha() 

        frame = self._frame()
        self.go.game.display.render(
            frame,
            target,
            position=self._draw_position(frame),
            scale=self.scale,
            shader = self.go.shaders['alpha'],
        )


class LogoLoadingOverlay(AnimatedImageOverlay):
    sprites = None

    def __init__(self, game_objects, **kwargs):
        default_pos = (game_objects.game.window_size[0] - 24, game_objects.game.window_size[1] - 24)

        super().__init__(
            game_objects,
            LogoLoadingOverlay.sprites['idle'],
            pos=kwargs.pop('pos', default_pos),
            frame_time=kwargs.pop('frame_time', 0.1),
            fade_in=kwargs.pop('fade_in', 0.1),
            hold=kwargs.pop('hold', 0.9),
            fade_out=kwargs.pop('fade_out', 0.2),
            channel=kwargs.pop('channel', 'save_point'),
            scale=kwargs.pop('scale', 1.0),
            anchor=kwargs.pop('anchor', 'bottom_right'),
            **kwargs,
        )

    @staticmethod
    def pool(game_objects):
        LogoLoadingOverlay.sprites = read_files.load_sprites_dict('assets/sprites/ui/overlay/logo_loading/', game_objects)