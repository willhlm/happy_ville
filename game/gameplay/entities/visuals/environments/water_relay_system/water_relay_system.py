import pygame
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects

class WaterRelaySystem(LayeredObjects):
    """The map-facing arrow that presents a relay's persistent direction."""
    animations = {}

    def __init__(self, pos, game_objects, parallax, layer_name, **props):
        live_blur = props.get("live_blur", False)
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.relay_id = str(props["relay_id"])
        self.angle_offset = float(props.get("visual_angle_offset", 0))
        self.init_sprites("assets/sprites/entities/visuals/environments/water_relay/")
        self.image = self.sprites['idle'][0]
        self.animation.play('idle')               
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        controller = self.game_objects.world_controller.water_relays
        state = controller.register(
            self.relay_id,
            state_level=props.get("state_level") or self.game_objects.map.biome_room_name,
            wind_network=props.get("wind_network", "golden_fields_liquid"),
            initial_angle=props.get("initial_angle", 0),
            lever_signal_id=props.get("lever_signal_id"),
        )
        self.angle = state["angle"] + self.angle_offset
        controller.subscribe(self.relay_id, self._on_relay_changed)

    def release_texture(self):
        self.game_objects.world_controller.water_relays.unsubscribe(
            self.relay_id, self._on_relay_changed
        )

    def _on_relay_changed(self, *, angle, **kwargs):
        self.angle = angle + self.angle_offset

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))               
        self.game_objects.game.display.render(self.image, target, position = pos, angle = self.angle)#shader render      
