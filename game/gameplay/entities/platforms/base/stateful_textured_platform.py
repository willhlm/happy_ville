import pygame

from engine.system import animation
from gameplay.entities.platforms.base.toggle_platform_states import STATE_TYPES
from gameplay.entities.platforms.texture.textured_platform import TexturedPlatform


class StatefulTexturedPlatform(TexturedPlatform):
    def __init__(self, pos, game_objects, initial_state):
        super().__init__(pos, game_objects)
        self.sprites = self.load_sprites()
        self.image = self.sprites[initial_state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.animation = animation.Animation(self)
        self.set_toggle_state(initial_state)

    def load_sprites(self):
        raise NotImplementedError

    def set_collision_enabled(self, enabled):
        self.hitbox = self.rect.copy()
        if not enabled:
            self.hitbox.width = 0
            self.hitbox.height = 0

    def set_toggle_state(self, state_name):
        self.currentstate = STATE_TYPES[state_name](self)


class WorldStateDrivenPlatform(StatefulTexturedPlatform):
    world_state_group = ""

    def __init__(self, pos, game_objects, **kwargs):
        self.id_key = kwargs.get("id")#the key used to store the state of this platform in the world state
        self.signal_key = kwargs.get("signal_id", self.id_key)#the key used to subscribe to signals that toggle this platform's state, defaults to the id_key if not provided
        initial_erect = game_objects.world_state.objects.load_bool(
            game_objects.map.biome_room_name,
            self.world_state_group,
            self.id_key,
            initial=kwargs.get("erect", False),
        )
        initial_state = "erect" if initial_erect else "down"
        super().__init__(pos, game_objects, initial_state=initial_state)

        if self.signal_key is not None:
            self.game_objects.signals.subscribe(self.signal_key, self.handle_signal)

    def _set_erect_state(self, erect):
        self.game_objects.world_state.objects.set_bool(
            self.game_objects.map.biome_room_name,
            self.world_state_group,
            self.id_key,
            erect,
        )
    
    def open(self):
        if type(self.currentstate).__name__ == "DownState":
            return
        self._set_erect_state(False)
        self.currentstate.handle_input("transform")

    def close(self):
        if type(self.currentstate).__name__ == "ErectState":
            return
        self._set_erect_state(True)
        self.currentstate.handle_input("transform")

    def toggle(self):
        self._set_erect_state(
            not self.game_objects.world_state.objects.load_bool(
                self.game_objects.map.biome_room_name,
                self.world_state_group,
                self.id_key,
            )
        )
        self.currentstate.handle_input("transform")

    def handle_signal(self, **kwargs):
        action = kwargs["action"]
        if action == "open":
            self.open()
        elif action == "close":
            self.close()
        elif action == "toggle":
            self.toggle()
