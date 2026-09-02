"""Windmill-network-powered piston platform."""

import pygame

from engine.system import animation
from engine.utils import read_files
from gameplay.entities.platforms.components.states_time_collision import Gone, Idle
from gameplay.entities.platforms.texture.textured_platform import TexturedPlatform

class Piston(TexturedPlatform):
    """A standalone piston with a cycle driven by a windmill network.

    Tiled properties:
      wind_network: shared windmill-network ID (defaults to
        ``golden_fields_liquid``)
      piston_profile: piston profile ID (defaults to
        ``golden_fields_default``)
    """

    def __init__(self, pos, game_objects, **props):
        super().__init__(pos, game_objects)
        self.wind_network = str(props.get("wind_network", "golden_fields_liquid"))
        self.piston_profile_id = str(props.get("piston_profile", "golden_fields_default"))
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/platforms/piston/", game_objects)
        self.image = self.sprites["idle"][0]
        size = (self.image.width, 5)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.true_pos = list(self.rect.topleft)
        self.animation = animation.Animation(self)
        self.currentstate = Idle(self)

        self.timers = game_objects.timer_manager
        self._timer_id = f"piston:{id(self)}"
        self.periodic_phase = float(props.get("periodic_phase", 0.0)) % 1.0

        controller = game_objects.world_controller.golden_fields
        self._set_turning_count(controller.windmill_turning_count(self.wind_network))
        controller.subscribe_windmill_network(self.wind_network, self._on_network_changed)

    def kill(self):
        self.game_objects.world_controller.golden_fields.unsubscribe_windmill_network(
            self.wind_network, self._on_network_changed
        )
        self.timers.remove_ID_timer(self._timer_id)
        super().kill()

    def _on_network_changed(self, *, turning_count, **kwargs):
        self._set_turning_count(turning_count)

    def _set_turning_count(self, turning_count):
        profile = self.game_objects.world_controller.golden_fields.piston_profile(
            self.piston_profile_id, self.wind_network, turning_count
        )
        if profile.get("mode") == "always_visible":
            self.timers.remove_ID_timer(self._timer_id)
            self.currentstate = Idle(self)
            return

        self.visible_time = profile["visible_time"]
        self.hidden_time = profile["hidden_time"]
        self.warning_time = profile.get("warning_time", 0)
        self._restart_cycle()

    def _restart_cycle(self):
        self.timers.remove_ID_timer(self._timer_id)
        self.currentstate = Idle(self)
        cycle_time = self.visible_time + self.warning_time + self.hidden_time
        if cycle_time <= 0:
            return

        elapsed = self.periodic_phase * cycle_time
        if elapsed < self.visible_time:
            self.timers.start_timer(self.visible_time - elapsed, self._begin_warning, ID=self._timer_id)
        elif elapsed < self.visible_time + self.warning_time:
            self.currentstate.handle_input("warning")
            self.timers.start_timer(
                self.visible_time + self.warning_time - elapsed, self._disappear, ID=self._timer_id
            )
        else:
            self.currentstate = Gone(self)
            self.timers.start_timer(cycle_time - elapsed, self._reappear, ID=self._timer_id)

    def _begin_warning(self):
        self.currentstate.handle_input("warning")
        self.timers.start_timer(self.warning_time, self._disappear, ID=self._timer_id)

    def _disappear(self):
        self.currentstate.handle_input("dissapear")
        self.timers.start_timer(self.hidden_time, self._reappear, ID=self._timer_id)

    def _reappear(self):
        self.currentstate.handle_input("re_appear")
        self.timers.start_timer(self.visible_time, self._begin_warning, ID=self._timer_id)
