from gameplay.entities.shared.components.hit import hit_effects


class PlayerHazardResolver:
    def __init__(self, player):
        self.player = player

    def handle_void(self, attacker, damage=1, after_transport=None):
        if self.player.game_objects.transition.is_busy:
            return

        self._begin_safe_respawn(after_transport=after_transport)
        self._apply_void_effect(attacker, damage)

    def handle_crush(self, attacker, damage=1):
        if self.player.game_objects.transition.is_busy:
            return

        self._begin_safe_respawn()
        self._apply_void_effect(attacker, damage)
        if not self.player.game_objects.transition.is_busy:
            self.player.platform_collider.enabled = True

    def _begin_safe_respawn(self, after_transport=None):
        if self.player.vitals.health <= 1:
            return

        self.player.currentstate.enter_state('invisible')

        def after():
            self.player.currentstate.handle_input('pray_post')
            if after_transport:
                after_transport()

        self.player.game_objects.transition.run(
            previous_state=self.player.game_objects.game.state_manager.state_stack[-1],
            style="alpha",
            action=self._move_to_safe_spawn,
            after=after,
            fade_length=60,
        )

    def _move_to_safe_spawn(self):
        self.player.reset_movement()
        self.player.body.set_pos(self.player.backpack.map.spawn_point['safe_spawn'])
        self.player.currentstate.enter_state('crouch', phase='main')

    def _apply_void_effect(self, attacker, damage):
        effect = getattr(attacker, '_hazard_effect', None)
        if effect is None:
            effect = hit_effects.create_contact_effect(
                self.player.game_objects,
                damage=damage,
                hit_type='void',
                hitstop=40,
                knockback=[0, 0],
                attacker=attacker,
                attacker_dir=[0, 0],
            )
            effect.attacker_callbacks = {}
            attacker._hazard_effect = effect

        effect = effect.copy()
        self.player.take_hit(effect)
