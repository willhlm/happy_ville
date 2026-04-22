import random
import pygame
from engine.utils import read_files


class ItemInteractComponent:
    def __init__(self, item, **kwarg):
        self.item = item
        self._interacting_player = None

        self.spawn_mode = kwarg.get('spawn_mode', 'idle')
        self.spawn_velocity = kwarg.get('spawn_velocity', None)
        self.spawn_velocity_range = kwarg.get('spawn_velocity_range', [0, 0])
        self.light_radius = kwarg.get('light_radius', 0)
        self._apply_spawn()

    def _apply_spawn(self):
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
        self.item.pickup_component.interact(self.item, player)
        self.item.game_objects.game.state_manager.enter_state(
            state_name='blit_image_text',
            image=self.item.sprites['idle'][0],
            text=self.item.description,
            callback=self.on_pickup_text_exit,
        )

    def on_pickup_text_exit(self):
        self._interacting_player.currentstate.handle_input('pray_post')

    def on_kill(self):
        if hasattr(self.item, 'light'):
            self.item.light.kill()


def pool_interactable_sprite(cls, game_objects):
    cls.sprites['wild'] = read_files.load_sprites_list('assets/sprites/entities/items/interactable_items/idle/', game_objects).textures
