import random, math
import behaviour_tree

#peace
class Target_position(behaviour_tree.Leaf):#calculate where to go
    def __init__(self,entity,method='horizontal'):
        super().__init__(entity)
        self.method = {'circle':self.circle,'horizontal':self.horizontal}[method]
        self.angle = random.randint(0,180)
        self.amp = 60
        self.update()

    def horizontal(self):
        distance = random.choice([-1,1])*random.randint(100,200)# + self.entity.game_objects.game.WINDOW_SIZE[0]*0.5
        self.entity.AI.black_board['target_position'] = [distance,0]

    def circle(self):
        self.amp = random.randint(self.amp-20,self.amp+20)
        self.amp = min(self.amp,80)#cap the amp

        offset = [-20-10*self.entity.dir[0],20-10*self.entity.dir[0]]
        self.angle = random.randint(self.angle+offset[0],self.angle+offset[1])

        self.entity.AI.black_board['target_position'] = [self.amp*math.cos(math.pi*self.angle/180),self.amp*math.sin(math.pi*self.angle/180)]

    def update(self):
        self.method()
        return 'SUCCESS'

class Patrol(behaviour_tree.Leaf):#try to go to target
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 400 #a time out timer

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        target_position = [self.entity.original_pos[0] + self.entity.AI.black_board['target_position'][0],self.entity.original_pos[1] + self.entity.AI.black_board['target_position'][1]]
        self.entity.patrol(target_position)

        if abs(target_position[0]-self.entity.rect.centerx) < 10 and abs(target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            return 'SUCCESS'
        elif self.entity.collision_types['left'] or self.entity.collision_types['right'] or self.entity.collision_types['top']:
            return 'FAILURE'
        elif self.time < 0:
            self.time = 400
            return 'FAILURE'
        else:
            return 'RUNNING'#no new posiion

class Look_target(behaviour_tree.Leaf):#look at target for patrolling
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        target_position = [self.entity.original_pos[0] + self.entity.AI.black_board['target_position'][0],self.entity.original_pos[1] + self.entity.AI.black_board['target_position'][1]]

        if target_position[0] - self.entity.rect.centerx >= 0 and self.entity.dir[0] == -1 or target_position[0] - self.entity.rect.centerx < 0 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            return 'FAILURE'
        elif target_position[1] - self.entity.rect.centery >= 0 and self.entity.dir[1] == 1 or target_position[1] - self.entity.rect.centery < 0 and self.entity.dir[1] == -1:#e.g. player jumpt over entity
            return 'FAILURE'
        return 'SUCCESS'

class Check_ground(behaviour_tree.Leaf):#check if there is ground in fron of entity
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        point = [self.entity.hitbox.midbottom[0] + self.entity.dir[0]*self.entity.hitbox[3],self.entity.hitbox.midbottom[1] + 8]
        collide = self.entity.game_objects.collisions.check_ground(point)
        if collide:#if collide: there is ground in front
            return 'SUCCESS'
        else:#there is no ground in front
            return 'FAILURE'

class Turn_around(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.dir[0] = -self.entity.dir[0]
        return 'SUCCESS'

#aggro
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

class Check_sight(behaviour_tree.Leaf):#check if target is within sight
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.AI.black_board['player_distance'] = [self.entity.AI.black_board['target'].rect.centerx-self.entity.rect.centerx,self.entity.AI.black_board['target'].rect.centery-self.entity.rect.centery]#check plater distance
        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.aggro_distance[0] and abs(self.entity.AI.black_board['player_distance'][1]) < self.entity.aggro_distance[1]:#within aggro distance
            return 'SUCCESS'#the giveup timer needs to be resetted here
        else:#no player around
            return 'FAILURE'

class Giveup_timer(behaviour_tree.Leaf):
    def __init__(self,entity,time = 300):
        super().__init__(entity)
        self.time = time
        self.timer = 0

    def reset_timer(self):
        self.timer = self.time

    def update(self):
        self.timer -= self.entity.game_objects.game.dt
        if self.timer < 0:
            self.reset_timer()
            return 'FAILURE'
        return 'SUCCESS'

class Chase(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.chase()
        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.attack_distance[0] and abs(self.entity.AI.black_board['player_distance'][1]) < self.entity.attack_distance[1]:
            return 'SUCCESS'
        else:
            return 'RUNNING'

class Attack_init(behaviour_tree.Leaf):#run once
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.currentstate.enter_state('Attack_pre')#shoul it be handle_input?
        self.entity.AI.black_board['attack'] = 'RUNNING'
        return 'SUCCESS'

class Attack(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        print('fe')
        return self.entity.AI.black_board['attack']

    def handle_input(self,input):
        if input == 'Attack':
            self.entity.AI.black_board['attack'] = 'SUCCESS'

class Look_player(behaviour_tree.Leaf):#look at player for aggro. Migawari or player
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.AI.black_board['player_distance'][0] > 0 and self.entity.dir[0] == -1 or self.entity.AI.black_board['player_distance'][0] < 0 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            return 'FAILURE'
        return 'SUCCESS'

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

def build_tree(entity):#peace and aggro: the peace will patrol around the spawn area. The aggro will chase player
    entity.AI = behaviour_tree.Treenode()

    peace = behaviour_tree.Sequence()
    peace2 = behaviour_tree.Success2Run()
    selector = behaviour_tree.Selector()
    run2success = behaviour_tree.Run2Success()
    selector.add_child(Look_target(entity))
    sequence = behaviour_tree.Sequence()
    sequence.add_child(Wait(entity))
    sequence.add_child(Turn_around(entity))
    sequence.add_child(Wait(entity))
    selector.add_child(sequence)
    peace.add_child(Target_position(entity))
    peace.add_child(selector)
    running_sequence = behaviour_tree.Running_sequence()
    invert = behaviour_tree.Inverter()
    invert.add_child(Check_sight(entity))
    running_sequence.add_child(invert)
    selector = behaviour_tree.Selector()
    fail2success = behaviour_tree.Fail2Success()
    sequence1 = behaviour_tree.Running_sequence()

    selector.add_child(Check_ground(entity))
    sequence = behaviour_tree.Sequence()
    success2fail = behaviour_tree.Success2Fail()
    sequence.add_child(Wait(entity))
    sequence.add_child(Turn_around(entity))
    sequence.add_child(Wait(entity))
    success2fail.add_child(sequence)
    selector.add_child(success2fail)
    sequence1.add_child(selector)
    sequence1.add_child(Patrol(entity))

    fail2success.add_child(sequence1)

    running_sequence.add_child(fail2success)
    peace.add_child(running_sequence)
    peace2.add_child(peace)

    aggro = behaviour_tree.Sequence()
    aggro.add_child(Select_target(entity))
    aggro1 = behaviour_tree.Running_sequence()
    aggro.add_child(aggro1)
    aggro2 = behaviour_tree.Selector()
    selector = behaviour_tree.Selector()
    selector.add_child(Check_sight(entity))
    selector.add_child(Giveup_timer(entity))
    aggro1.add_child(selector)
    aggro1.add_child(aggro2)
    aggro2.add_child(Look_player(entity))
    sequence = behaviour_tree.Sequence()
    sequence.add_child(Wait(entity))
    sequence.add_child(Turn_around(entity))
    sequence.add_child(Wait(entity))
    aggro2.add_child(sequence)
    aggro1.add_child(Chase(entity))
    aggro4 = behaviour_tree.Sequence()
    aggro.add_child(aggro4)
    aggro4.add_child(Attack_init(entity))
    aggro4.add_child(Attack(entity))
    aggro.add_child(Wait(entity))

    entity.AI.add_child(aggro)
    entity.AI.add_child(peace2)

    entity.AI.print_tree()

def build_tree_peace(entity):#no aggro, just roam around
    entity.AI = behaviour_tree.Treenode()

    peace = behaviour_tree.Sequence()

    succeeder = behaviour_tree.Fail2Success()
    run2success = behaviour_tree.Run2Success()#patrol
    succeeder.add_child(Look_target(entity))

    peace.add_child(Target_position(entity))
    peace.add_child(Wait(entity))
    peace.add_child(succeeder)

    running_sequence = behaviour_tree.Running_sequence()

    selector = behaviour_tree.Selector()
    selector.add_child(Check_ground(entity))
    sequence = behaviour_tree.Sequence()
    sequence.add_child(Wait(entity))
    sequence.add_child(Turn_around(entity))
    sequence.add_child(Wait(entity))
    selector.add_child(sequence)
    running_sequence.add_child(selector)
    running_sequence.add_child(Patrol(entity))

    peace.add_child(running_sequence)
    entity.AI.add_child(peace)

    entity.AI.print_tree()
