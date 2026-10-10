"""Power-source-driven piston platform."""

import pygame

from engine.system import animation
from engine.utils import read_files
from gameplay.entities.platforms.components.states_time_collision import Gone, Idle
from gameplay.entities.platforms.texture.textured_platform import TexturedPlatform
from gameplay.world.configs.golden_fields_systems import piston_profile

class Piston(TexturedPlatform):
    """A standalone piston with a cycle driven by a named power source.

    Tiled properties:
      power_source: registered power-source ID (defaults to
        ``golden_fields_windmills``)
      relay_angle: required direction when power_source is a water relay
      piston_profile: piston profile ID (defaults to
        ``golden_fields_default``)
    """

    def __init__(self, pos, game_objects, **props):
        super().__init__(pos, game_objects)
        self.power_source = str(
            props.get("power_source", "golden_fields_windmills")
        ).strip()
        self.relay_angle = int(props.get("relay_angle", 90)) % 360
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

        controller = game_objects.world_controller.power
        self._set_powered(controller.is_powered(
            self.power_source, relay_angle=self.relay_angle
        ))
        controller.subscribe(
            self.power_source,
            self._on_power_source_changed,
            relay_angle=self.relay_angle,
        )
        self._power_subscribed = True

    def kill(self):
        self._dispose()
        super().kill()

    def release_texture(self):
        self._dispose()
        super().release_texture()

    def _dispose(self):
        if self._power_subscribed:
            self.game_objects.world_controller.power.unsubscribe(
                self.power_source,
                self._on_power_source_changed,
                relay_angle=self.relay_angle,
            )
            self._power_subscribed = False
        self.timers.remove_ID_timer(self._timer_id)

    def _on_power_source_changed(self, *, powered, **kwargs):
        self._set_powered(powered)

    def _set_powered(self, powered):
        profile = piston_profile(
            self.piston_profile_id, powered
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
