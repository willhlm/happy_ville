import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables


class ProgressionStatue(Interactables):
    sprite_path = None
    preview_sprite = None

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict(self.sprite_path, game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.refresh_state()

    def is_complete(self):
        raise NotImplementedError

    def grant_progression(self):
        raise NotImplementedError

    def get_text(self):
        raise NotImplementedError

    def refresh_state(self):
        self.interacted = self.is_complete()
        if self.interacted:
            self.shader_state.add_shader('tint', colour=[0, 0, 0, 100])
        self.text = self.get_text()

    def interact(self):
        if self.interacted:
            return

        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.grant_progression()
        self.refresh_state()
        if self.interacted:
            self.shader_state.add_shader('tint', colour=[0, 0, 0, 100])

        self.game_objects.game.state_manager.enter_state(
            state_name='Blit_image_text',
            image=self.game_objects.player.sprites[self.preview_sprite][0],
            text=self.text,
            callback=self.on_exit,
        )

    def on_exit(self):
        self.game_objects.player.currentstate.handle_input('Pray_post')
