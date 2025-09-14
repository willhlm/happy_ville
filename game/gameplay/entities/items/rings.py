import pygame
from engine.utils import read_files
from gameplay.entities.items.base.interactable_item import InteractableItem

class Rings(InteractableItem):#ring in which to attach radnas
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Rings.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.level = 1
        self.description = 'A ring'
        self.radna = None

    def set_finger(self, finger):
        self.finger = finger
        self.animation.play(self.finger + '_' + str(self.level))

    def update_equipped(self):#caleld from neckalce
        self.radna.equipped()

    def handle_press_input(input):#called from neckalce
        self.radna.handle_press_input(input)

    def upgrade(self):
        self.level += 1
        self.animation.play(self.finger + '_' + str(self.level))

    def pickup(self, player):
        super().pickup(player)
        player.backpack.radna.add_ring(self)
        self.set_owner(player)

    def attach_radna(self, radna):
        self.radna = radna
        self.radna.set_owner(self.entity)
        self.radna.attach()

    def detach_radna(self, radna):
        self.radna.detach()
        self.radna.set_owner(None)
        self.radna = None

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/rings/',game_objects)
        super().pool(game_objects)