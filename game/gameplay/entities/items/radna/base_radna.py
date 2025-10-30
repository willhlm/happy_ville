from gameplay.entities.items.base.interactable_item import InteractableItem

class Radna(InteractableItem):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.description = ''#for inventory
        self.level = 1#the level of ring reuried to equip
        self.entity = None#defualt is no owner

    def equipped(self):#called from the rings, when rings are updated
        pass

    def handle_press_input(input):#called from neckalce
        pass

    def pickup(self, player):
        super().pickup(player)
        copy_item = type(self)([0,0], self.game_objects)
        player.backpack.radna.add(copy_item)
        self.game_objects.signals.emit('item_interacted', item = self, player = player)

    def detach(self):#called when de-taching the radna to ring
        self.shader = None#for ui

    def attach(self):#called when attaching the radna to ring
        self.shader = self.game_objects.shaders['colour'] #for ui