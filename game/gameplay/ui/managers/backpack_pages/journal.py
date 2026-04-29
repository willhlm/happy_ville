import pygame

from gameplay.ui.loaders import JournalLoader

from .base import BaseUI


class JournalUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.journal_UI = JournalLoader(game_objects)
        self.define_pointer(game_objects)
        self.journal_index = [0, 0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8

        self.define_enemies()
        self.select_enemies()

    def on_enter(self, **kwarg):
        super().on_enter(**kwarg)
        self.enemies = []
        self.journal_index = [0, 0]
        self.enemy_index = self.journal_index.copy()
        self.define_enemies()
        self.select_enemies()

    def define_enemies(self):
        for enemy in self.game_objects.world_state.statistics_state.statistics['kill']:
            enemy = self.game_objects.registry.fetch('enemies', enemy)(
                [0, 0], self.game_objects
            )
            self.enemies.append(enemy)

    def select_enemies(self):
        self.selected_enemies = self.enemies[
            self.enemy_index[0]:self.enemy_index[0] + self.number:1
        ]

    def define_pointer(self, game_objects):
        size = [48, 16]
        self.pointer = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.rect(
            self.pointer,
            [200, 50, 50, 255],
            (0, 0, size[0], size[1]),
            width=1,
            border_radius=5,
        )
        self.pointer = game_objects.game.display.surface_to_texture(self.pointer)

    def render(self):
        self.game_objects.ui.backpack.screen.clear(0, 0, 0, 0)
        self.blit_journal_BG()
        self.blit_names()
        self.blit_pointer()
        self.blit_enemy()
        self.blit_description()
        self.blit_screen()

    def blit_journal_BG(self):
        self.game_objects.game.display.render(self.journal_UI.BG, self.game_objects.ui.backpack.screen)

    def blit_names(self):
        for index, enemy in enumerate(self.selected_enemies):
            name = enemy.__class__.__name__
            self.game_objects.font.render(
                self.game_objects.ui.backpack.screen,
                name,
                position=self.journal_UI.name_pos[index],
                width=152,
                letter_frame=100,
            )

    def blit_pointer(self):
        pos = [
            self.journal_UI.name_pos[self.journal_index[0]][0],
            self.journal_UI.name_pos[self.journal_index[0]][1] - 5,
        ]
        self.game_objects.game.display.render(
            self.pointer, self.game_objects.ui.backpack.screen, position=pos
        )

    def blit_enemy(self):
        enemy = self.selected_enemies[self.journal_index[0]]
        enemy.rect.midbottom = self.journal_UI.image_pos
        enemy.animation.update()
        self.game_objects.game.display.render(
            enemy.image,
            self.game_objects.ui.backpack.screen,
            position=[
                enemy.rect.center[0] - enemy.rect.width * 0.5,
                enemy.rect.center[1] - enemy.rect.height * 0.5,
            ],
        )

    def blit_description(self):
        self.conv = self.selected_enemies[self.journal_index[0]].description
        self.game_objects.font.render(
            self.game_objects.ui.backpack.screen,
            self.conv,
            position=(380, 120),
            width=152,
            letter_frame=int(self.letter_frame // 2),
        )

    def handle_events(self, input):
        input.processed()
        if input.pressed:
            if input.name == 'select':
                self.exit_state()
            elif input.name == 'rb':
                pass
            elif input.name == 'lb':
                self.previous_page(screen_alpha=230)
            elif input.name == 'down':
                self.letter_frame = 0
                self.journal_index[0] += 1
                if self.journal_index[0] == self.number:
                    self.enemy_index[0] += 1
                    self.enemy_index[0] = min(
                        self.enemy_index[0],
                        len(self.enemies) - self.number,
                    )
                    self.select_enemies()
                self.journal_index[0] = min(
                    self.journal_index[0],
                    len(self.selected_enemies) - 1,
                )
            elif input.name == 'up':
                self.letter_frame = 0
                self.journal_index[0] -= 1
                if self.journal_index[0] == -1:
                    self.enemy_index[0] -= 1
                    self.enemy_index[0] = max(0, self.enemy_index[0])
                    self.select_enemies()
                self.journal_index[0] = max(0, self.journal_index[0])
