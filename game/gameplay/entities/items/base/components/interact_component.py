import random


class ItemInteractComponent:
    def __init__(self, item, **kwarg):
        self.item = item
        self._interacting_player = None

        self.spawn_mode = kwarg.get('spawn_mode', 'idle')
        self.spawn_velocity = kwarg.get('spawn_velocity', None)
        self.spawn_velocity_range = kwarg.get('spawn_velocity_range', [0, 0])
        self.light_radius = kwarg.get('light_radius', 0)
        self.apply_spawn()

    def apply_spawn(self):
        if self.spawn_velocity is not None:
            self.item.velocity = [
                random.uniform(
                    self.spawn_velocity[0] - self.spawn_velocity_range[0],
                    self.spawn_velocity[0] + self.spawn_velocity_range[0],
                ),
                random.uniform(
                    self.spawn_velocity[1] - self.spawn_velocity_range[1],
                    self.spawn_velocity[1] + self.spawn_velocity_range[1],
                ),
            ]

        if self.light_radius > 0:
            self.item.light = self.item.game_objects.lights.add_light(self.item, radius=self.light_radius)

    def apply_visual_spawn_mode(self):
        animation_name = self.spawn_mode if self.spawn_mode in self.item.sprites else 'idle'
        self.item.image = self.item.sprites[animation_name][0]
        self.item.animation.play(animation_name)

    def interact_with_pickup_text(self, player):
        self._interacting_player = player
        self.start_pickup_feedback(player)
        self.item.game_objects.game.state_manager.enter_state(
            state_name='dynamic_overlay',
            loader_key='item_pickup',
            image=self.item.get_pickup_image(),
            title=self.item.get_pickup_title(),
            text=self.item.get_pickup_text(),
            callback=self.on_pickup_text_exit,
        )

    def start_pickup_feedback(self, player):
        pickup_fx = self.item.get_pickup_fx()

        fade_config = pickup_fx.get('fade')
        if fade_config:
            fade_kwargs = fade_config.copy()
            fade_state = fade_kwargs.pop('state', 'Alpha')
            fade_kwargs.setdefault('on_complete', lambda: None)
            self.item.shader_state.enter_state(fade_state, **fade_kwargs)

        sound_config = pickup_fx.get('sound')
        if sound_config:
            sound_key = sound_config.get('key', 'interact')
            volume = sound_config.get('volume', 0.4)
            self.item.game_objects.sound.play_item_sound(sound_key, volume=volume)

        particle_config = pickup_fx.get('particles')
        if particle_config:
            self.item.game_objects.particles.emit(
                particle_config.get('preset', 'burst'),
                pos=self.item.hitbox.center,
                n=particle_config.get('count', 18),
                colour=particle_config.get('colour', [255, 255, 255, 255]),
            )

    def on_pickup_text_exit(self):
        self.item.on_pickup_interaction_complete(self._interacting_player)
        self._interacting_player.currentstate.handle_input('pray_post')

    def on_kill(self):
        if hasattr(self.item, 'light'):
            self.item.light.kill()
