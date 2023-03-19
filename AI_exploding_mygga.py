import sys, random, math

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [0,0]
        self.init_time = 0

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.init_time += 0.02*self.entity.game_objects.game.dt
        self.update_AI()

    def update_AI(self):
        pass

##peace states
class Nothing(AI):#can be used in cutscene etc
    def __init__(self,entity):
        super().__init__(entity)

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.children = {'Walk':Walk,'Wait':Wait,'Turn_around':Turn_around}
        self.set_child('Wait')

    def set_child(self,child):#the init will run the same frame but its update in the next
        self.child = self.children[child](self)

    def update_AI(self):#the init will run the same frame but its update in the next
        self.child.update_AI()

    def set_parent(self,parent):
        self.enter_AI(parent)

class Walk():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.handle_input('Walk')
        self.init_time = 0

    def update_AI(self):
        self.init_time += 0.02*self.parent.entity.game_objects.game.dt
        self.parent.entity.velocity[0] += 0.1*self.parent.entity.dir[0]
        self.parent.entity.velocity[1] += -0.2*math.sin(self.init_time*5)+self.parent.player_distance[1]*0.001
        self.check_sight()
        self.exit()

    def check_sight(self):
        if abs(self.parent.player_distance[0])<self.parent.entity.aggro_distance and abs(self.parent.player_distance[1])<self.parent.entity.aggro_distance*0.2:
            self.parent.set_parent('Aggro')

    def exit(self):
        if self.init_time > math.pi:
            child = random.choice(list(self.parent.children.keys()))
            self.parent.set_child(child)

class Wait():#the entity should just stay and do nothing for a while
    def __init__(self,parent,duration=100):
        super().__init__()
        self.parent = parent
        self.duration = duration
        self.parent.entity.currentstate.enter_state('Idle')

    def update_AI(self):
        self.duration -= 1
        if self.duration < 0:
            self.exit()

    def exit(self):#check sight
        self.parent.set_child('Turn_around')

class Turn_around():#when the player jumps over, should be a delays before the entity turns around
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.dir[0] = -self.parent.entity.dir[0]

    def update_AI(self):
        self.parent.set_child('Walk')

class Aggro(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.children = {'Chase':Chase,'Wait_aggro':Wait_aggro,'Turn_around_aggro':Turn_around_aggro,'Attack':Attack}
        self.set_child('Chase')
        self.timers = []
        self.timer_jobs = Giveup_timer(self,300)#if player is out of sight for more than duration, go to peace, else, remain

    def set_child(self,child):#the init will run the same frame but its update in the next
        self.child = self.children[child](self)

    def update_AI(self):
        self.check_sight()
        self.child.update_AI()
        self.update_timers()

    def set_parent(self,parent):#the init will run the same frame but its update in the next
        self.enter_AI(parent)

    def check_sight(self):#if wihtin sight, stay in chase
        if abs(self.player_distance[0])<self.entity.aggro_distance and abs(self.player_distance[1])<self.entity.aggro_distance*0.3:
            self.timer_jobs.restore()
        else:#out of sight
            self.timer_jobs.activate()

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def handle_input(self,input,duration=100):
        self.child.handle_input(input)

class Chase():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.handle_input('Walk')
        self.init_time = 0

    def update_AI(self):
        self.look_player()#make the direction along the player. a delay can be added
        self.chase_momvement()
        self.attack()#are we withtin attack distance?

    def look_player(self):#look at the player
        if self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.set_child('Wait_aggro')

    def chase_momvement(self):
        self.init_time += 0.02*self.parent.entity.game_objects.game.dt
        self.parent.entity.velocity[0] += self.parent.entity.dir[0]*0.3#*abs(math.sin(self.init_time))
        self.parent.entity.velocity[1] += -self.parent.entity.dir[1]*0.3*math.sin(self.init_time*5)+self.parent.player_distance[1]*0.001

    def attack(self):
        if abs(self.parent.player_distance[0])<self.parent.entity.attack_distance and abs(self.parent.player_distance[1])<self.parent.entity.attack_distance:
            self.parent.set_child('Attack')

class Turn_around_aggro():#when the player jumps over, should be a delays before the entity turns around
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.dir[0] = -self.parent.entity.dir[0]

    def update_AI(self):
        self.parent.set_child('Chase')

class Wait_aggro():#the entity should just stay and do nothing for a while
    def __init__(self,parent,duration=50):
        self.parent = parent
        self.duration = duration
        self.parent.entity.currentstate.enter_state('Idle')

    def update_AI(self):
        self.duration -= 1
        if self.duration < 0:
            self.exit()

    def exit(self):
        if self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.set_child('Turn_around_aggro')
        else:
            self.parent.set_child('Chase')

class Attack():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.handle_input('explode')
        self.parent.entity.velocity = [0,1]#compensate for gravity

    def update_AI(self):
        pass

    def handle_input(self,input):
        if input == 'De_explode':#called when deexplode animation is finished
            self.parent.set_child('Wait_aggro')

class Giveup_timer():
    def __init__(self,AI,duration = 100):
        self.AI = AI
        self.duration = duration

    def restore(self):
        self.lifetime = self.duration

    def activate(self):#add timer to the entity timer list
        if self in self.AI.timers: return#do not append if the timer is already inside
        self.restore()
        self.AI.timers.append(self)

    def deactivate(self):
        self.AI.timers.remove(self)
        self.AI.set_parent('Peace')

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 0:
            self.deactivate()
