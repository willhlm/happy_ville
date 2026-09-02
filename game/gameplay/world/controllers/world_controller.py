"""Derived world-condition controllers.

Persistent facts belong in ``World_state``.  This module combines those facts
into named, runtime conditions (for example, whether the Golden Fields wind is
currently blowing) and broadcasts only when the derived result changes.
"""

from .golden_fields_controller import GoldenFieldsController
from .water_relay_controller import WaterRelayController


class WorldController:
    """Registry and notifier for named, derived world conditions.

    A condition is a no-argument callable returning a truthy/falsy value.
    Consumers should read its initial value with :meth:`is_enabled` and then
    subscribe to it for live changes.  Conditions themselves are deliberately
    not saved: their inputs are the saved world facts.
    """

    SIGNAL_PREFIX = "world_condition:"
    WIND_AVAILABLE = "wind_available"
    # This is the persistent boss ID, not necessarily the Python class name.
    WIND_BOSS_ID = "bieggs"

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._resolvers = {}
        self._states = {}
        self._region_controllers = []
        self.configure_global_wind(self.WIND_BOSS_ID)
        self.golden_fields = GoldenFieldsController(game_objects, self)
        self.water_relays = WaterRelayController(game_objects, self)

    @classmethod
    def signal_name(cls, condition_id):
        return f"{cls.SIGNAL_PREFIX}{condition_id}"

    def register(self, condition_id, resolver, *, replace=False):
        """Register a condition and cache its current state.

        Registration does not emit a signal.  A newly spawned object must
        query ``is_enabled`` during setup, which also makes room reloads
        deterministic.
        """
        if not callable(resolver):
            raise TypeError("A world-condition resolver must be callable.")
        if condition_id in self._resolvers and not replace:
            raise ValueError(f"World condition '{condition_id}' is already registered.")

        self._resolvers[condition_id] = resolver
        self._states[condition_id] = bool(resolver())
        return self._states[condition_id]

    def unregister(self, condition_id):
        """Remove a condition when its owning map/system is unloaded."""
        self._resolvers.pop(condition_id, None)
        self._states.pop(condition_id, None)

    def is_registered(self, condition_id):
        return condition_id in self._resolvers

    def is_enabled(self, condition_id):
        """Return the cached current state of a registered condition."""
        try:
            return self._states[condition_id]
        except KeyError as error:
            raise KeyError(f"Unknown world condition '{condition_id}'.") from error

    def refresh(self, condition_id):
        """Re-evaluate a condition and notify listeners if it changed."""
        try:
            enabled = bool(self._resolvers[condition_id]())
        except KeyError as error:
            raise KeyError(f"Unknown world condition '{condition_id}'.") from error

        previous = self._states[condition_id]
        self._states[condition_id] = enabled
        if enabled != previous:
            self.game_objects.signals.emit(
                self.signal_name(condition_id),
                condition_id=condition_id,
                enabled=enabled,
            )
        return enabled

    def refresh_all(self):
        """Re-evaluate global conditions and notify region controllers."""
        conditions = {
            condition_id: self.refresh(condition_id)
            for condition_id in tuple(self._resolvers)
        }
        for controller in tuple(self._region_controllers):
            controller.refresh()
        return conditions

    def register_region_controller(self, controller):
        """Register a map/region controller with a ``refresh`` method."""
        if controller not in self._region_controllers:
            self._region_controllers.append(controller)

    def unregister_region_controller(self, controller):
        if controller in self._region_controllers:
            self._region_controllers.remove(controller)

    def configure_global_wind(self, wind_boss_id):
        """Set the boss whose defeat permanently disables wind everywhere."""
        self.wind_boss_id = str(wind_boss_id)
        self.register(
            self.WIND_AVAILABLE,
            lambda: not self.game_objects.world_state.narrative.is_boss_defeated(self.wind_boss_id),
            replace=self.is_registered(self.WIND_AVAILABLE),
        )

    def subscribe(self, condition_id, listener):
        """Subscribe to future state changes for one condition."""
        if not self.is_registered(condition_id):
            raise KeyError(f"Unknown world condition '{condition_id}'.")
        self.game_objects.signals.subscribe(self.signal_name(condition_id), listener)

    def unsubscribe(self, condition_id, listener):
        self.game_objects.signals.unsubscribe(self.signal_name(condition_id), listener)
