from .biomes import Biome, get_biome_cls


class BiomeManager:
    """
    Owns: biome selection + active room configuration.
    Keeps biome polymorphism for object spawning and post-processing.
    """

    def __init__(self, loader_ref):
        self.loader = loader_ref
        self.current_biome_name = ""
        self.biome_changed = True
        self.current_room_id = ""
        self.biome = Biome(self.loader)

    def update_for_biome_room(self, biome_room_name: str):
        biome_name = biome_room_name[: biome_room_name.rfind("_")]
        self.biome_changed = biome_name != self.current_biome_name

        if self.biome_changed:
            self.current_biome_name = biome_name
            self.biome.clear_biome()
            self.biome = get_biome_cls(biome_name)(self.loader)

        self.current_room_id = biome_room_name[biome_room_name.rfind("_") + 1 :]
        self.biome.apply_room(self.current_room_id)

    def reset(self):
        self.biome.clear_biome()
        self.current_biome_name = ""
        self.current_room_id = ""
        self.biome_changed = True

    def set_camera(self, ctx):
        self.loader.game_objects.camera_manager.camera.reset_player_center()
        self.biome.set_camera(ctx)

    def configure_weather(self, group: str, parallax):
        self.biome.configure_weather(group, parallax)

    def configure_particles(self, group: str, parallax):
        self.biome.configure_particles(group, parallax)

    def post_process(self, group: str, parallax):
        self.biome.post_process(group, parallax)

    def load_biome_objects(self, data, parallax, offset, ctx, map_def, layer_name, viewport_center):
        self.biome.load_objects(data, parallax, offset, ctx, map_def, layer_name, viewport_center)
