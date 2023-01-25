import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.update_AI()

    def update_AI(self):
        pass

    def finish_action(self):#called when animation is finshed for a state
        pass

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update_AI(self):
        self.idle_momvement()
        self.check_sight()

    def idle_momvement(self):
        rand=random.randint(0,1000)
        if rand>970:
            self.entity.currentstate.handle_input('Idle')
            self.entity.dir[0] = -self.entity.dir[0]
        else:
            self.entity.currentstate.handle_input('Walk')

    def check_sight(self):#if wihtin sight, enter the passed AI
        if abs(self.player_distance[0])<self.entity.aggro_distance and abs(self.player_distance[1])<self.entity.aggro_distance*0.2:
            self.enter_AI('Chase')

class Nothing(AI):#for cutscenes
    def __init__(self,entity):
        super().__init__(entity)

class Pause(AI):#the entity should just stay and do nothing for a while
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.duration = duration
        self.entity.currentstate.handle_input('Idle')

    def update_AI(self):
        self.duration -= self.entity.game_objects.game.dt
        if self.duration < 0:
            self.exit()

    def exit(self):
        self.entity.AI = Chase(self.entity,0)#send in the turnaround duration för the next fram. So that pause and turn_around do run in sequence.

class Trun_around(Pause):#when the player jumps over, should be a delays before the entity turns around
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def exit(self):
        self.entity.dir[0] = -self.entity.dir[0]
        self.enter_AI('Chase')

class Chase(AI):
    def __init__(self,entity, turn_delay = 50):
        super().__init__(entity)
        self.entity.currentstate.handle_input('Walk')
        self.timers = []
        self.timer_jobs = Giveup_timer(self,100)#if player is out of sight for more than duration, go to peace, else, remain
        self.turn_delay = turn_delay

    def update_AI(self):
        if self.look_player(): return#make the direction along the player. a delay can be added
        self.check_sight()#are we within aggro distance?
        self.attack()#are we withtin attack distance?
        self.update_timers()
        self.turn_delay = 50

    def attack(self):
        if abs(self.player_distance[0])<self.entity.attack_distance and abs(self.player_distance[1])<self.entity.attack_distance*0.2:
            self.enter_AI('Attack')

    def check_sight(self):#if wihtin sight, enter the passed AI
        if abs(self.player_distance[0])<self.entity.aggro_distance and abs(self.player_distance[1])<self.entity.aggro_distance*0.2:
            self.timer_jobs.restore()
        else:#out of sight
            self.timer_jobs.activate()

    def look_player(self):#look at the player
        if self.player_distance[0] > 0 and self.entity.dir[0] == -1 or self.player_distance[0] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.entity.AI = Trun_around(self.entity,self.turn_delay)
            return True#do not go to attack if you just turned around

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Attack(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.handle_input('Attack')

    def finish_action(self):#called when animation is finished
        self.entity.AI = Pause(self.entity,50)

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
        self.AI.enter_AI('Peace')

    def update(self):
        self.lifetime -= self.AI.entity.game_objects.game.dt
        if self.lifetime < 0:
            self.deactivate()
