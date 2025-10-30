from gameplay.entities.items.base.interactable_item import InteractableItem

class InfinityStones(InteractableItem):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sword = kwarg.get('entity', None)
        self.description = ''

    def set_pos(self, pos):#for inventory
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self, player):#called from sword when balcksmith attached the stone
        pass

    def pickup(self, player):
        super().pickup(player)
        self.attach(player)
        self.sword = player.sword