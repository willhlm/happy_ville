import pygame

class FontManager():
    FONT_PATH = 'assets/sprites/utils/fonts/8BitSnobbery.ttf'
    TEXT_BG_PATHS = {
        'default': 'assets/sprites/utils/text_bg5.png',
        'text_bubble': 'assets/sprites/utils/text_bg4.png',
    }
    FONT_STYLES = {
        'text': 12,
        'title': 24,
    }

    def __init__(self, game_objects):
        self.game_objects = game_objects
        display = game_objects.game.display
        self.atlases = {
            style: display.make_font_atlas(
                font_path=self.FONT_PATH,
                font_size=font_size,
            )
            for style, font_size in self.FONT_STYLES.items()
        }
        self.text_bg_textures = {
            key: display.load_texture(path)
            for key, path in self.TEXT_BG_PATHS.items()
        }

    def get_atlas(self, style='text'):
        return self.atlases[style]

    def get_height(self, style='text'):
        return self.get_atlas(style).linesize

    def measure(self, text='', style='text'):
        return self.get_atlas(style).font.size(text)

    def render(self, target, text='', *, letter_frame=None, color=(255, 255, 255, 255), scale=1.0, alignment='left', position=(0, 0), width=None, style='text'):
        self.game_objects.game.display.render_text(self.get_atlas(style), target, text or '', letter_frame=letter_frame, color=color, scale=scale, alignment=alignment, position=position, width=width)

    def render_text_bg(self, target, surface_size, *, position=(0, 0), bg_type='default'):#does 9 draw calls. Fine for UI stuff
        source = self.text_bg_textures[bg_type]
        src_w, src_h = source.width, source.height
        if src_w % 3 != 0 or src_h % 3 != 0:
            raise ValueError(f"Text background '{bg_type}' must have dimensions divisible by 3.")

        corner_w = src_w // 3
        corner_h = src_h // 3
        dst_w, dst_h = surface_size

        left_w = min(corner_w, dst_w)
        right_w = min(corner_w, max(0, dst_w - left_w))
        center_w = max(0, dst_w - left_w - right_w)

        top_h = min(corner_h, dst_h)
        bottom_h = min(corner_h, max(0, dst_h - top_h))
        center_h = max(0, dst_h - top_h - bottom_h)
        src_x = (0, corner_w, src_w - corner_w)
        # `section` sampling uses texture-space Y, which is flipped relative to
        # the source image's top-left pixel coordinates.
        src_y = (src_h - corner_h, corner_h, 0)
        dst_x = (position[0], position[0] + left_w, position[0] + dst_w - right_w)
        dst_y = (position[1], position[1] + top_h, position[1] + dst_h - bottom_h)
        dst_cols = (left_w, center_w, right_w)
        dst_rows = (top_h, center_h, bottom_h)

        for row in range(3):
            for col in range(3):
                target_w = dst_cols[col]
                target_h = dst_rows[row]
                if target_w <= 0 or target_h <= 0:
                    continue

                self.game_objects.game.display.render(source, target, position=(dst_x[col], dst_y[row]), scale=(target_w / corner_w, target_h / corner_h), section=pygame.Rect(src_x[col], src_y[row], corner_w, corner_h))
