from .base_overlay import BaseOverlay


class ItemPickupToast(BaseOverlay):
    """A short bottom-left notification shown after an item is collected."""

    def __init__(
        self,
        game_objects,
        image,
        item_name,
        *,
        fade_in=0.2,
        hold=1.25,
        fade_out=0.35,
        channel='item_pickup',
        margin=12,
        icon_size=32,
    ):
        self.game_objects = game_objects
        self.image = image
        self.item_name = str(item_name)
        self.fade_in = float(fade_in)
        self.hold = float(hold)
        self.fade_out = float(fade_out)
        self.channel = channel
        self.margin = int(margin)
        self.icon_size = int(icon_size)
        self.fade = game_objects.fade.create('alpha', 0)

        self.elapsed = 0.0
        self.done = False
        self._lifetime = self.fade_in + self.hold + self.fade_out

    def on_start(self):
        pass

    def update(self, dt):
        self.elapsed += float(dt)
        if self.elapsed >= self._lifetime:
            self.done = True

    def _alpha(self):
        if self.fade_in > 0 and self.elapsed < self.fade_in:
            alpha = self.elapsed / self.fade_in
        elif self.elapsed < self.fade_in + self.hold:
            alpha = 1.0
        else:
            fade_elapsed = self.elapsed - self.fade_in - self.hold
            alpha = 1.0 - (fade_elapsed / self.fade_out if self.fade_out > 0 else 1.0)
        return int(255 * max(0.0, min(1.0, alpha)))

    def draw(self, target):
        alpha = self._alpha()
        max_dimension = max(self.image.width, self.image.height, 1)
        image_scale = self.icon_size / max_dimension
        image_width = self.image.width * image_scale
        image_height = self.image.height * image_scale
        image_y = target.height - self.margin - image_height

        self.fade.set(alpha)
        self.fade.render(
            self.image,
            target,
            position=(self.margin, image_y),
            scale=image_scale,
        )

        text_height = self.game_objects.font.get_height()
        text_y = target.height - self.margin - (image_height + text_height) * 0.5
        self.game_objects.font.render(
            target,
            self.item_name,
            position=(self.margin + image_width + 8, text_y),
            color=(255, 255, 255, alpha),
            letter_frame=None,
        )
