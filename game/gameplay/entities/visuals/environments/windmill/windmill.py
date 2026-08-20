import pygame
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects
from . import states

class Windmill(LayeredObjects):
    animations = {}
    STATES = frozenset({"idle", "stuck", "active"})
    WORLD_STATE_GROUP = "windmill"

    def __init__(self, pos, game_objects, parallax, layer_name, id, initial_state="idle", live_blur=False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.id = str(id)
        self.init_sprites("assets/sprites/entities/visuals/environments/windmill/")
        state = self.game_objects.world_state.objects.load_value(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, initial=initial_state)
        # Loading a map-provided initial state can change Golden Fields'
        # derived windmill-network counts before any interactable is used.
        self.game_objects.world_controller.refresh_all()
        self.image = self.sprites['idle'][0]
        self.animation.play('idle')
        self.saved_state = state
        self.apply_wind_state(self.game_objects.world_controller.is_enabled(
            self.game_objects.world_controller.WIND_AVAILABLE
        ))
        
        self.game_objects.signals.subscribe(self.id, self.handle_signal)
        self.game_objects.world_controller.subscribe(
            self.game_objects.world_controller.WIND_AVAILABLE, self._on_wind_changed
        )
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

    def set_state(self, state: str):
        """Persist a new state; this instance updates immediately."""
        self.game_objects.world_state.objects.set_value(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, state)
        self.saved_state = state
        self.apply_wind_state(self.game_objects.world_controller.is_enabled(
            self.game_objects.world_controller.WIND_AVAILABLE
        ))
        self.game_objects.world_controller.refresh_all()

    def enter_state(self, state):        
        self.currentstate = states.STATE_TYPES[state](self)

    def handle_signal(self, *, state, **kwargs):
        self.set_state(state)

    def _on_wind_changed(self, *, enabled, **kwargs):
        self.apply_wind_state(enabled)

    def apply_wind_state(self, wind_available):
        state = self.saved_state if wind_available else "idle"
        self.enter_state(state)

    def release_texture(self):
        # Map cleanup must remove this bound listener before a new map is loaded.
        self.game_objects.signals.unsubscribe(self.id, self.handle_signal)
        self.game_objects.world_controller.unsubscribe(
            self.game_objects.world_controller.WIND_AVAILABLE, self._on_wind_changed
        )

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))               
        self.game_objects.game.display.render(self.image, target, position = pos, angle = self.currentstate.angle)#shader render      
