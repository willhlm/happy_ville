import math, random

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

#decorators
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

#peace
class Target_position(Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.angle = random.randint(0,180)
        self.amp = 60
        self.update()

    def update(self):
        self.amp = random.randint(self.amp-20,self.amp+20)
        self.amp = min(self.amp,80)#cap the amp

        offset = [-20-10*self.entity.dir[0],20-10*self.entity.dir[0]]
        self.angle = random.randint(self.angle+offset[0],self.angle+offset[1])

        self.entity.AI.black_board['target_position'] = [self.amp*math.cos(math.pi*self.angle/180),self.amp*math.sin(math.pi*self.angle/180)]
        return 'SUCCESS'

class Patrol(Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        target_position = [self.entity.original_pos[0] + self.entity.AI.black_board['target_position'][0],self.entity.original_pos[1] + self.entity.AI.black_board['target_position'][1]]

        self.entity.velocity[0] += 0.001*(target_position[0]-self.entity.rect.centerx)+0.02*self.entity.dir[0]
        self.entity.velocity[0] = math.copysign(1,self.entity.velocity[0])*min(abs(self.entity.velocity[0]),1)#limit the max abs velocity to 1
        self.entity.velocity[1] += 0.001*(target_position[1]-self.entity.rect.centery)

        if abs(target_position[0]-self.entity.rect.centerx) < 10 and abs(target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            return 'SUCCESS'
        elif self.entity.collision_types['left'] or self.entity.collision_types['right'] or self.entity.collision_types['bottom'] or self.entity.collision_types['top']:
            return 'FAILURE'
        else:
            return 'RUNNING'#no new posiion

class Look_target(Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        target_position = [self.entity.original_pos[0] + self.entity.AI.black_board['target_position'][0],self.entity.original_pos[1] + self.entity.AI.black_board['target_position'][1]]

        if target_position[0] - self.entity.rect.centerx > 10 and self.entity.dir[0] == -1 or target_position[0] - self.entity.rect.centerx < -10 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            self.entity.dir[0] = -self.entity.dir[0]
            return 'FAILURE'
        elif target_position[1] - self.entity.rect.centery > 10 and self.entity.dir[1] == 1 or target_position[1] - self.entity.rect.centery < -10 and self.entity.dir[0] == -1:#e.g. player jumpt over entity
            self.entity.dir[1] = -self.entity.dir[1]
            return 'FAILURE'
        return 'SUCCESS'

#aggro
class Select_target(Leaf):#selects the one that is the closest in players group (so aila or migawari)
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        min_disatnce = 1000000
        target = None
        for player in self.entity.game_objects.players:
            distance = abs(self.entity.rect.centerx - player.rect.centerx)
            if distance < min_disatnce:
                min_distance = distance
                target = player
        self.entity.AI.black_board['target'] = target
        return 'SUCCESS'

class Check_sight(Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.timer = 0#give up timer

    def update(self):
        self.timer -= self.entity.game_objects.game.dt
        self.entity.AI.black_board['player_distance'] = [self.entity.AI.black_board['target'].rect.centerx-self.entity.rect.centerx,self.entity.AI.black_board['target'].rect.centery-self.entity.rect.centery]#check plater distance
        if abs(self.entity.AI.black_board['player_distance'][0])<self.entity.aggro_distance and abs(self.entity.AI.black_board['player_distance'][1])<self.entity.aggro_distance*0.5:#within aggro distance
            self.timer = 300#reset
            return 'SUCCESS'
        elif self.timer < 0:#no player around
            self.timer = 0
            return 'FAILURE'

class Chase(Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.init_time = 0

    def update(self):
        self.init_time += 0.02*self.entity.game_objects.game.dt

        self.entity.velocity[0] += self.entity.dir[0]*0.3#*abs(math.sin(self.init_time))
        self.entity.velocity[1] += -self.entity.dir[1]*0.3*math.sin(self.init_time*5) + self.entity.AI.black_board['player_distance'][1]*0.001

        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.attack_distance and abs(self.entity.AI.black_board['player_distance'][1]) < self.entity.attack_distance:
            return 'SUCCESS'
        else:
            return 'RUNNING'

class Attack(Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.state = 'RUNNING'

    def update(self):
        state = self.state
        if self.state != 'RUNNING':
            self.state = 'RUNNING'#reset
        else:
            self.entity.currentstate.handle_input('explode')
        return state

    def handle_input(self,input):
        if input == 'De_explode':
            self.state = 'FAILURE'
        elif input == 'Attack':
            self.state = 'SUCCESS'

class Look_player(Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.AI.black_board['player_distance'][0] > 0 and self.entity.dir[0] == -1 or self.entity.AI.black_board['player_distance'][0] < 0 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            self.entity.dir[0] = -self.entity.dir[0]
            return 'FAILURE'
        return 'SUCCESS'

class Wait(Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = 100

    def update(self):
        self.duration -= 1
        if self.duration < 0:
            self.duration = 100#reset
            return 'SUCCESS'
        else:
            return 'RUNNING'

def build_tree(entity):
    entity.AI = Treenode()

    peace = Sequence()
    succeeder = Fail2Success()
    run2success = Run2Success()#patrol
    succeeder.add_child(Look_target(entity))
    peace.add_child(succeeder)
    selector = Selector()
    success2fail = Success2Fail()
    success2fail.add_child(Patrol(entity))
    selector.add_child(run2success)
    selector.add_child(Target_position(entity))
    run2success.add_child(success2fail)
    peace.add_child(selector)

    aggro = Sequence()
    aggro.add_child(Select_target(entity))
    aggro1 = Running_sequence()
    aggro.add_child(aggro1)
    aggro2 = Selector()
    aggro1.add_child(Check_sight(entity))
    aggro1.add_child(aggro2)
    aggro2.add_child(Look_player(entity))
    aggro2.add_child(Wait(entity))
    aggro1.add_child(Chase(entity))
    aggro4 = Fail2Success()
    aggro.add_child(aggro4)
    aggro4.add_child(Attack(entity))
    aggro.add_child(Wait(entity))

    entity.AI.add_child(aggro)
    entity.AI.add_child(peace)

    entity.AI.print_tree()
