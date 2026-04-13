from copy import deepcopy

from engine.utils import read_files

from gameplay.world.weather import weather

from ..room_config import RoomConfig, merge_room_configs


class Biome:
    default_room_config = RoomConfig()
    room_configs = {}

    def __init__(self, map_loader):
        self.level = map_loader
        self.live_blur = False
        self.weather_config = {}
        self.active_room_id = None
        self._current_music_signature = None
        self._weather_registry = {
            "wind": {
                "manager": self.level.game_objects.weather.wind,
                "fx_class": "WindFX",
            },
            "rain": {
                "manager": self.level.game_objects.weather.rain,
                "fx_class": "RainFX",
            },
            "fog": {
                "manager": self.level.game_objects.weather.fog,
                "fx_class": "FogFX",
            },
            "snow": {
                "manager": self.level.game_objects.weather.snow,
                "fx_class": "SnowFX",
            },
        }

    def clear_biome(self):
        pass

    def set_camera(self, ctx):
        pass

    def post_process(self, group, parallax):
        pass

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        pass

    def get_room_config(self, room_id: str) -> RoomConfig:
        return merge_room_configs(self.default_room_config, self.room_configs.get(room_id))

    def on_room_loaded(self, room_id: str, config: RoomConfig):
        pass

    def apply_room(self, room_id: str):
        self.active_room_id = room_id
        self.live_blur = False
        self.weather_config = {}

        config = self.get_room_config(room_id)

        if config.live_blur is not None:
            self.live_blur = config.live_blur

        if config.weather is not None:
            self.weather_config = deepcopy(config.weather)

        self._apply_music(config.music or [])

        if config.ambient_light is not None:
            self.level.game_objects.lights.set_ambient_light(config.ambient_light)

        for light_kwargs in config.player_lights or []:
            self.level.game_objects.lights.add_light(self.level.game_objects.player, **light_kwargs)

        self.on_room_loaded(room_id, config)

    def _apply_music(self, tracks):
        signature = tuple((track.folder, track.key, track.index, track.volume, track.loop, track.fade) for track in tracks)
        if signature == self._current_music_signature:
            return

        self._current_music_signature = signature
        for track in tracks:
            sounds = read_files.load_sounds_dict(track.folder)
            self.level.game_objects.sound.play_background_sound(
                sounds[track.key][0],
                index=track.index,
                loop=track.loop,
                fade=track.fade,
                volume=track.volume,
            )

    def configure_weather(self, group, parallax):
        for weather_type in self.weather_config.keys():
            if self.weather_config[weather_type]["layers"].get(group, False):
                kwarg = self.weather_config[weather_type]["layers"][group]
                self._weather_registry[weather_type]["manager"].configure(group, kwarg)
                new_weather = getattr(weather, self._weather_registry[weather_type]["fx_class"])(
                    self.level.game_objects, parallax=parallax, layer_name=group, **kwarg
                )

                self._weather_registry[weather_type]["manager"].add_fx(new_weather)
                if group.startswith("fg"):
                    self.level.game_objects.all_fgs.add(group, new_weather)
                else:
                    self.level.game_objects.all_bgs.add(group, new_weather)
