import math, random
import behaviour_tree

#peace
class Target_position(behaviour_tree.Leaf):
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

class Patrol(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        target_position = [self.entity.original_pos[0] + self.entity.AI.black_board['target_position'][0],self.entity.original_pos[1] + self.entity.AI.black_board['target_position'][1]]
        self.entity.patrol(target_position)
        if abs(target_position[0]-self.entity.rect.centerx) < 10 and abs(target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            return 'SUCCESS'
        elif self.entity.collision_types['left'] or self.entity.collision_types['right'] or self.entity.collision_types['bottom'] or self.entity.collision_types['top']:
            return 'FAILURE'
        else:
            return 'RUNNING'#no new posiion

class Look_target(behaviour_tree.Leaf):
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

class Check_sight(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)
        self.timer = 0#give up timer

    def update(self):
        self.timer -= self.entity.game_objects.game.dt
        self.entity.AI.black_board['player_distance'] = [self.entity.AI.black_board['target'].rect.centerx-self.entity.rect.centerx,self.entity.AI.black_board['target'].rect.centery-self.entity.rect.centery]#check plater distance
        if abs(self.entity.AI.black_board['player_distance'][0])<self.entity.aggro_distance[0] and abs(self.entity.AI.black_board['player_distance'][1])<self.entity.aggro_distance[1]:#within aggro distance
            self.timer = 300#reset
            return 'SUCCESS'
        elif self.timer < 0:#no player around
            self.timer = 0
            return 'FAILURE'

class Chase(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.chase()

        if abs(self.entity.AI.black_board['player_distance'][0]) < self.entity.attack_distance[0] and abs(self.entity.AI.black_board['player_distance'][1]) < self.entity.attack_distance[1]:
            return 'SUCCESS'
        else:
            return 'RUNNING'

class Attack(behaviour_tree.Leaf):
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

class Look_player(behaviour_tree.Leaf):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.AI.black_board['player_distance'][0] > 0 and self.entity.dir[0] == -1 or self.entity.AI.black_board['player_distance'][0] < 0 and self.entity.dir[0] == 1:#e.g. player jumpt over entity
            self.entity.dir[0] = -self.entity.dir[0]
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

def build_tree(entity):
    entity.AI = behaviour_tree.Treenode()

    peace = behaviour_tree.Sequence()
    succeeder = behaviour_tree.Fail2Success()
    run2success = behaviour_tree.Run2Success()#patrol
    succeeder.add_child(Look_target(entity))
    peace.add_child(succeeder)
    selector = behaviour_tree.Selector()
    success2fail = behaviour_tree.Success2Fail()
    success2fail.add_child(Patrol(entity))
    selector.add_child(run2success)
    selector.add_child(Target_position(entity))
    run2success.add_child(success2fail)
    peace.add_child(selector)

    aggro = behaviour_tree.Sequence()
    aggro.add_child(Select_target(entity))
    aggro1 = behaviour_tree.Running_sequence()
    aggro.add_child(aggro1)
    aggro2 = behaviour_tree.Selector()
    aggro1.add_child(Check_sight(entity))
    aggro1.add_child(aggro2)
    aggro2.add_child(Look_player(entity))
    aggro2.add_child(Wait(entity))
    aggro1.add_child(Chase(entity))
    aggro4 = behaviour_tree.Fail2Success()
    aggro.add_child(aggro4)
    aggro4.add_child(Attack(entity))
    aggro.add_child(Wait(entity))

    entity.AI.add_child(aggro)
    entity.AI.add_child(peace)

    #entity.AI.print_tree()
