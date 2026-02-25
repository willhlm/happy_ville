# =========================
# text_overlay.py
# =========================
from .base_overlay import BaseOverlay


class TextOverlay(BaseOverlay):
    def __init__(
        self,
        game_objects,
        lines,
        *,
        box_left: int,
        box_top: int,
        box_width: int,
        line_gap: int = 16,
        alignment: str = "center",
        fade_in: float = 0.25,
        hold: float = 2.0,
        fade_out: float = 0.35,
        delay: float = 0.0,
        channel: str | None = None,
    ):
        self.go = game_objects
        self.lines = list(lines)

        self.box_left = int(box_left)
        self.box_top = int(box_top)
        self.box_width = int(box_width)
        self.line_gap = int(line_gap)
        self.alignment = alignment

        self.fade_in = float(fade_in)
        self.hold = float(hold)
        self.fade_out = float(fade_out)
        self.delay = float(delay)

        self.t = 0.0
        self.done = False
        self.channel = channel

        self._lifetime = max(0.0, self.fade_in + self.hold + self.fade_out)

        # sound gating: play once when the text actually becomes visible
        self._sound_played = False

    def on_start(self) -> None:
        # Intentionally do nothing here, because we want the sound to respect delay
        # (sound will fire when t crosses delay in update()).
        pass

    def update(self, dt: float) -> None:
        self.t += float(dt)

        # Fire sound once, exactly when the overlay starts displaying (after delay)
        if (not self._sound_played) and (self.t >= self.delay):
            self._sound_played = True
            self.go.sound.play_ui_sound("narrative_text")

        if self.t >= self.delay + self._lifetime:
            self.done = True

    def _local_t(self) -> float:
        return max(0.0, self.t - self.delay)

    def _alpha(self) -> int:
        if self.t < self.delay:
            return 0

        t = self._local_t()
        if self.fade_in > 0 and t < self.fade_in:
            a = t / self.fade_in
        elif t < self.fade_in + self.hold:
            a = 1.0
        else:
            out_t = t - (self.fade_in + self.hold)
            a = 1.0 - (out_t / self.fade_out if self.fade_out > 0 else 1.0)

        a = max(0.0, min(1.0, a))
        return int(255 * a)

    def draw(self, target) -> None:
        if self.t < self.delay:
            return

        alpha = self._alpha()
        win_w, win_h = self.go.game.window_size
        sx = (target.width / win_w) 
        sy = (target.height / win_h)
        font_scale = 0.5 * (sx + sy)

        for i, line in enumerate(self.lines):
            self.go.game.display.render_text(
                self.go.font.font_atals,
                target,
                line,
                position=(self.box_left * sx, (self.box_top + i * self.line_gap) * sy),
                width=self.box_width * sx,
                alignment=self.alignment,
                color=(255, 255, 255, alpha),
                letter_frame=None,
                scale=font_scale,
            )
