from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform
from gameplay.entities.platforms.components.platform_components import COMPONENTS

"""Custom properties accepted from Tiled.

Collision / traversal:
solid: bool
oneway_up: bool
crushes_entities: bool

Damage:
damage: str
damage_on_land: bool
knockback_x: str
knockback_y: str

Movement:
move: bool
move_type: str -> direction_distance, path
distance: str
direction: str
phase: str
speed: str
pingpong: bool
loop: bool
path: int -> path object id
snap_to_path: bool
snap_mode: str -> closest, start
smooth: bool
samples_per_segment: int

Float on liquid:
float_on_liquid: bool
float_offset: str
buoyancy: str
water_damping: str
float_gravity: str
max_rise_speed: str
max_fall_speed: str
edge_margin: str
bob_amplitude: str
bob_speed: str
bob_phase: str
landing_bob_impulse: str
max_landing_bob_impulse: str
landing_min_speed: str
landing_splash_particles: int
jump_off_bob_impulse: str
max_jump_off_bob_impulse: str
jump_off_min_speed: str
jump_off_splash_particles: int

Disappear / respawn:
disappear_on_stand: bool
disappear_time: int
respawn_time: int

Breakable:
breakable: bool
vulnerable_sides: str -> "top", "bottom", "left", "right"
health: str
invincibility_time: str

Signals / visuals:
sprite_path: str
signal_id: str -> subscribes to this signal
ID: str -> emitted by breakable platforms on destroy
"""

def parse_components(components):
    if isinstance(components, (list, tuple)):
        return [str(x).strip() for x in components if str(x).strip()]
    s = str(components).strip()
    if not s:
        return []
    return [c.strip() for c in s.split(",") if c.strip()]

def parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}

class ComponentPlatform(DynamicPlatform):
    def __init__(self, pos, game_objects, components, **props):
        super().__init__(pos, game_objects, size=props.get('size', (16, 16)), components=[])
        self.props = props
        self.crushes_entities = parse_bool(props.get('crushes_entities', True), default=True)

        name = props.get("sprite_path", "generic/default")
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
            if cls is None:
                raise KeyError(f"Unknown platform component: {comp_name}")
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
