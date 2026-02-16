from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform
from gameplay.entities.platforms.components.components import COMPONENTS

def parse_components(components):
    if isinstance(components, (list, tuple)):
        return [str(x).strip() for x in components if str(x).strip()]
    s = str(components).strip()
    if not s:
        return []
    return [c.strip() for c in s.split(",") if c.strip()]

class GenericPlatform(DynamicPlatform):
    def __init__(self, pos, game_objects, components, **props):
        super().__init__(pos, game_objects, size=props.get('size', (16, 16)), components=[])
        self.props = props

        name = props.get("sprite_path", "generic/default/")
        self.sprites = read_files.load_sprites_dict(f"assets/sprites/entities/platforms/{name}" + '/', game_objects)
        self.image = self.sprites["idle"][0]

        # sync rect/hitbox to image size
        self.rect.width = self.image.width
        self.rect.height = self.image.height
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()

        # ---- components ----
        names = parse_components(components)
        self.components = []
        for comp_name in names:
            cls = COMPONENTS.get(comp_name)
            self.components.append(cls(self, **self.props))

        for c in self.components:
            c.on_added()

    def kill(self):
        self.components = []
        super().kill()            

    def draw(self, target):
        self.game_objects.game.display.render(self.image,target,
            position=(
                int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]),
                int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1]),
            ),
        )        