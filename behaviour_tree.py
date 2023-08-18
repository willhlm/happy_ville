import random

class Treenode():
    def __init__(self):
        self.children = []
        self.parent = None
        self.curr_child = 0
        self.black_board = {'player_distance':[0,0],'target_position':[0,0],'target':None}#save stuff:

    def handle_input(self,input):
        self.children[self.curr_child].handle_input(input)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def update(self):
        #self.print_leaf()
        for i in range(self.curr_child, len(self.children)):
            response = self.children[i].update()
            if response == 'SUCCESS':
                self.curr_child = 0
                return#reset tree to first
            elif response == 'RUNNING':#need to remember what was runing for next, I think
                self.curr_child = i#shoudl go to this child again in the next tick
                return
            elif response == 'FAILURE':
                pass#next child
        self.curr_child = 0

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        spaces = ' ' * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else ""
        print(prefix + self.__class__.__name__)
        for child in self.children:
            child.print_tree()

    #for cutscene to do nothing
    def deactivate(self):
        self.save_children = self.children.copy()
        self.children = []

    def activate(self):
        self.children = self.save_children.copy()
        self.save_children = []

    def print_leaf(self):
        self.children[self.curr_child].print_leaf()

class Sequence(Treenode):#returns FAILURE or RUNNING prematurly
    def __init__(self):
        super().__init__()

    def update(self):
        for i in range(self.curr_child, len(self.children)):
            response = self.children[i].update()
            if response == 'FAILURE':
                self.curr_child = 0
                return 'FAILURE'#reset
            elif response == 'RUNNING':
                self.curr_child = i
                return 'RUNNING'
        self.curr_child = 0
        return 'SUCCESS'#reset

class Running_sequence(Treenode):#reset the run on running
    def __init__(self):
        super().__init__()

    def update(self):
        for i in range(self.curr_child, len(self.children)):
            response = self.children[i].update()
            if response == 'FAILURE':
                self.curr_child = 0
                return 'FAILURE'#reset
            elif response == 'RUNNING':
                self.curr_child = 0
                return 'RUNNING'
        self.curr_child = 0
        return 'SUCCESS'#reset

class Selector(Treenode):#returns SUCCESS or RUNNING prematurly
    def __init__(self):
        super().__init__()

    def update(self):
        for i in range(self.curr_child, len(self.children)):
            response = self.children[i].update()
            if response == 'SUCCESS':
                self.curr_child = 0
                return 'SUCCESS'
            elif response == 'RUNNING':
                self.curr_child = i
                return 'RUNNING'
        self.curr_child = 0
        return 'FAILURE'

class Random_selector(Treenode):#returns SUCCESS or RUNNING prematurly
    def __init__(self):
        super().__init__()
        self.curr_child = None

    def random_child(self):
        if self.curr_child == None:#select rando child
            self.curr_child = random.randint(0,len(self.children)-1)

    def update(self):
        for i in range(0, len(self.children)):
            self.random_child()
            response = self.children[self.curr_child].update()
            if response == 'SUCCESS':
                self.curr_child = None#reset child
                return 'SUCCESS'
            elif response == 'RUNNING':
                return 'RUNNING'

        self.curr_child = None
        return 'FAILURE'#reset failed

#decorators, can have only one child
class Fail2Success(Treenode):#a decorator, returns sucess even if it failed
    def __init__(self):
        super().__init__()

    def update(self):
        response = self.children[0].update()
        if response == 'FAILURE':
            return 'SUCCESS'
        return response

class Success2Fail(Treenode):#a decorator, returns sucess even if it failed
    def __init__(self):
        super().__init__()

    def update(self):
        response = self.children[0].update()
        if response == 'SUCCESS':
            return 'FAILURE'
        return response

class Inverter(Treenode):#a decorator, returns sucess even if it failed
    def __init__(self):
        super().__init__()

    def update(self):
        response = self.children[0].update()
        if response == 'SUCCESS':
            return 'FAILURE'
        elif response == 'FAILURE':
            return 'SUCCESS'
        return response

class Run2Success(Treenode):#a decorator, running is turnde to sucess
    def __init__(self):
        super().__init__()

    def update(self):
        response = self.children[0].update()
        if response == 'RUNNING':
            return 'SUCCESS'
        return response

class Success2Run(Treenode):#a decorator, running is turnde to sucess
    def __init__(self):
        super().__init__()

    def update(self):
        response = self.children[0].update()
        if response == 'SUCCESS':
            return 'RUNNING'
        return response

class FPS_limiter(Treenode):
    def __init__(self):
        super().__init__()
        self.limit = 120

    def update(self):
        self.limit -= 1
        if self.limit < 0:
            self.limit = 120
            return 'SUCCESS'
        return 'FAILURE'

#leaves
class Leaf(Treenode):
    def __init__(self,entity):
        super().__init__()
        self.entity = entity

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def print_leaf(self):
        print(self)
