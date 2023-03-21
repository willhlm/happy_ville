import random
import behaviour_tree

class Select_target(behaviour_tree.Leaf):#selects the one that is the closest in players group (so aila or migawari)
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

class Look_player(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.AI.black_board['player_distance'] = [self.entity.AI.black_board['target'].rect.centerx-self.entity.rect.centerx,self.entity.AI.black_board['target'].rect.centery-self.entity.rect.centery]#check plater distance
        if self.entity.AI.black_board['player_distance'][0] > 0 and self.entity.dir[0] == -1 or self.entity.AI.black_board['player_distance'][0] < 0 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            return 'FAILURE'
        return 'SUCCESS'

class Turn_around(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.dir[0] = -self.entity.dir[0]
        return 'SUCCESS'

class Check_sight(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.attack_distance and abs(self.entity.AI.black_board['player_distance'][1])<self.entity.attack_distance:#within aggro distance
            return 'SUCCESS'
        return 'FAILURE'

class Chase(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity[0] += self.entity.dir[0]*0.3#*abs(math.sin(self.init_time))
        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.attack_distance and abs(self.entity.AI.black_board['player_distance'][1]) < self.entity.attack_distance:
            return 'SUCCESS'
        else:
            return 'FAILURE'

class Wait(behaviour_tree.Leaf):
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

class Init_attack_animation(behaviour_tree.Leaf):#run once
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.currentstate.enter_state('Attack_pre')
        return 'SUCCESS'

class Attack(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.state = 'RUNNING'

    def update(self):
        if self.state != 'RUNNING':
            state = self.state
            self.state = 'RUNNING'#reset
            return state
        return 'RUNNING'

    def handle_input(self,input):
        if input == 'Attack':
            self.state = 'SUCCESS'

class Init_jump_animation(behaviour_tree.Leaf):#run once
    def __init__(self,entity,sign = 1):
        super().__init__(entity)
        self.sign = sign

    def update(self):
        self.entity.AI.black_board['jump_direction'] = self.sign
        self.entity.currentstate.enter_state('Jump_pre')
        return 'SUCCESS'

class Jumping(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.state = 'RUNNING'
        self.counter = 1

    def update(self):
        if self.state != 'RUNNING':
            state = self.state
            self.state = 'RUNNING'#reset
            self.entity.AI.black_board['jump_direction'] = 1#reset
            return state
        return 'RUNNING'

    def handle_input(self,input):#when it finished attack, called when attack animation finished
        if input == 'Landed':#jump animation finsihed
            self.counter -= 1
            if self.counter > 0:
                self.entity.dir[0] = -self.entity.dir[0]
                self.entity.currentstate.enter_state('Jump_pre')
            else:
                self.counter = 1
                self.state = 'SUCCESS'

class Init_rangeattack_animation(behaviour_tree.Leaf):#run once
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.currentstate.enter_state('Special_attack_pre')
        return 'SUCCESS'

class Range_attack(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.state = 'RUNNING'

    def update(self):
        if self.state != 'RUNNING':
            state = self.state
            self.state = 'RUNNING'#reset
            return state
        return 'RUNNING'

    def handle_input(self,input):#when it finished attack, called when attack animation finished
        if input == 'Attack':#attack animation finished
            self.state = 'SUCCESS'

class Init_dash_animation(behaviour_tree.Leaf):#run once
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.currentstate.enter_state('Dash_pre')
        return 'SUCCESS'

class Dash_attack(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.state = 'RUNNING'

    def update(self):
        if self.state != 'RUNNING':
            state = self.state
            self.state = 'RUNNING'#reset
            return state
        return 'RUNNING'

    def handle_input(self,input):#when it finished attack, called when attack animation finished
        if input == 'Dash':#attack animation finished
            self.state = 'SUCCESS'

def build_tree(entity):
    entity.AI = behaviour_tree.Treenode()
    entity.AI.black_board['jump_direction'] = 1#add reindeer specific information ot the BB

    aggro = behaviour_tree.Sequence()
    aggro.add_child(Select_target(entity))
    selector = behaviour_tree.Selector()
    selector.add_child(Look_player(entity))
    selector.add_child(Turn_around(entity))
    aggro.add_child(selector)
    selector = behaviour_tree.Selector()
    aggro.add_child(selector)
    selector.add_child(Check_sight(entity))

    Random_selector = behaviour_tree.Random_selector()

    sequence = behaviour_tree.Sequence()
    sequence.add_child(Init_jump_animation(entity))
    sequence.add_child(Jumping(entity))
    sequence.add_child(Wait(entity))
    Random_selector.add_child(sequence)

    sequence = behaviour_tree.Sequence()
    sequence.add_child(Init_dash_animation(entity))
    sequence.add_child(Dash_attack(entity))
    sequence.add_child(Wait(entity))
    Random_selector.add_child(sequence)

    sequence = behaviour_tree.Sequence()
    sequence.add_child(Init_rangeattack_animation(entity))
    sequence.add_child(Range_attack(entity))
    sequence.add_child(Wait(entity))
    Random_selector.add_child(sequence)

    inverter = behaviour_tree.Inverter()
    inverter.add_child(Random_selector)
    selector.add_child(inverter)

    random_selector = behaviour_tree.Random_selector()

    sequence = behaviour_tree.Sequence()
    sequence.add_child(Init_attack_animation(entity))
    sequence.add_child(Attack(entity))
    sequence.add_child(Wait(entity))
    random_selector.add_child(sequence)

    sequence = behaviour_tree.Sequence()
    sequence.add_child(Init_jump_animation(entity,-1))#reverse jumping
    sequence.add_child(Jumping(entity))
    sequence.add_child(Wait(entity))
    random_selector.add_child(sequence)

    aggro.add_child(random_selector)
    entity.AI.add_child(aggro)

    entity.AI.print_tree()
