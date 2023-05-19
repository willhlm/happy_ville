import sys

class Inventory_states():
    def __init__(self, inventory):
        self.inventory = inventory
        self.state_name = str(type(self).__name__).lower()#the name of the class

    def handle_input(self,input):
        pass

    def enter_state(self,newstate):
        self.inventory.state = getattr(sys.modules[__name__], newstate)(self.inventory)#make a class based on the name of the newstate: need to import sys

class Items(Inventory_states):
    def __init__(self, inventory):
        super().__init__(inventory)
        self.inventory.define_pointer()

    def handle_input(self,input):
        if input[-1] =='right':
            self.inventory.item_index[0] += 1
            self.inventory.item_index[0] = min(self.inventory.item_index[0], len(self.inventory.items['items'])-1)

        elif input[-1] =='left':
            self.inventory.item_index[0] -= 1
            if self.inventory.item_index[0] < 0:
                self.inventory.item_index[0] = 0
                self.enter_state('Sword')

        elif input[-1] =='down':
            self.inventory.item_index[0] += 6
            self.inventory.item_index[0] = min(self.inventory.item_index[0], len(self.inventory.items['items'])-1)

        elif input[-1] =='up':
            self.inventory.item_index[0] -= 6
            if self.inventory.item_index[0] < 0:
                self.inventory.item_index[0] += 6*2
                #self.inventory.item_index = [len(self.inventory.pointer_pos['key_items'])-1,self.inventory.item_index[0]]
                self.enter_state('Key_items')

class Sword(Inventory_states):
    def __init__(self, inventory):
        super().__init__(inventory)
        size = self.inventory.items[self.state_name][self.inventory.item_index[0]].rect.size
        self.inventory.define_pointer([size[0],size[1]])

    def handle_input(self,input):
        if input[-1] =='right':
            if self.inventory.item_index[0] ==0:#if on bottom right
                self.enter_state('Items')
            elif self.inventory.item_index[0] ==1:#if in middle right
                self.inventory.item_index[0] = 0
                self.enter_state('Key_items')
            elif self.inventory.item_index[0] == 2:#if on top
                self.inventory.item_index[0] -= 1
            elif self.inventory.item_index[0] == 3:#if on middle left
                self.inventory.item_index[0] -= 2
            elif self.inventory.item_index[0] == 4:#if on bottom left
                self.inventory.item_index[0] -= 4

        elif input[-1] =='left':
            if self.inventory.item_index[0] ==0:#if on bottom right
                self.inventory.item_index[0] += 4
            elif self.inventory.item_index[0] ==1:#if in middle right
                self.inventory.item_index[0] += 2
            elif self.inventory.item_index[0] == 2:#if on top
                self.inventory.item_index[0] += 1
            elif self.inventory.item_index[0] == 3:#if on middle left
                pass
            elif self.inventory.item_index[0] == 4:#if on bottom left
                pass

        elif input[-1] =='down':
            if self.inventory.item_index[0] ==0:#if on bottom right
                pass
            elif self.inventory.item_index[0] ==1:#if in middle right
                self.inventory.item_index[0] -= 1
            elif self.inventory.item_index[0] == 2:#if on top
                self.inventory.item_index[0] -= 1
            elif self.inventory.item_index[0] == 3:#if on middle left
                self.inventory.item_index[0] += 1
            elif self.inventory.item_index[0] == 4:#if on bottom left
                pass

        elif input[-1] =='up':
            if self.inventory.item_index[0] ==0:#if on bottom right
                self.inventory.item_index[0] += 1
            elif self.inventory.item_index[0] ==1:#if in middle right
                self.inventory.item_index[0] += 1
            elif self.inventory.item_index[0] == 2:#if on top
                pass
            elif self.inventory.item_index[0] == 3:#if on middle left
                self.inventory.item_index[0] -= 1
            elif self.inventory.item_index[0] == 4:#if on bottom left
                self.inventory.item_index[0] -= 1

class Key_items(Inventory_states):
    def __init__(self, inventory):
        super().__init__(inventory)
        self.inventory.define_pointer()

    def handle_input(self,input):
        if input[-1] =='right':
            self.inventory.item_index[0] += 1
            self.inventory.item_index[0] = min(self.inventory.item_index[0], len(self.inventory.items['items'])-1)

        elif input[-1] =='left':
            self.inventory.item_index[0] -= 1
            if self.inventory.item_index[0] < 0:
                self.inventory.item_index[0] = 1
                self.enter_state('Sword')

        elif input[-1] =='down':
            self.inventory.item_index[0] += 6
            if self.inventory.item_index[0] > len(self.inventory.items['items'])-1:
                self.inventory.item_index[0] -= 6*2
                self.enter_state('Items')
            #self.inventory.item_index[0] = min(self.inventory.item_index[0],len(self.inventory.pointer_pos['items'])-1)

        elif input[-1] =='up':
            self.inventory.item_index[0] -= 6
            if self.inventory.item_index[0] < 0:
                self.inventory.item_index[0] = 0
