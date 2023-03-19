import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [entity.game_objects.player.rect.centerx-entity.rect.centerx,entity.game_objects.player.rect.centery-entity.rect.centery]#check plater distance

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.update_AI()

    def update_AI(self):
        pass

##peace states
class Nothing(AI):#can be used in cutscene etc
    def __init__(self,entity):
        super().__init__(entity)

class Aggro_1(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.children = {'Chase':Chase,'Wait_aggro':Wait_aggro,'Turn_around_aggro':Turn_around_aggro,'Attack':Attack,'Jumping':Jumping}
        self.set_child('Chase')

    def set_child(self,child):#the init will run the same frame but its update in the next
        self.child = self.children[child](self)

    def update_AI(self):
        self.child.update_AI()

    def set_parent(self,parent):#the init will run the same frame but its update in the next
        self.enter_AI(parent)

class Chase():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.handle_input('Walk')#this one is walking

    def update_AI(self):
        self.look_player()
        self.chase_momvement()

    def chase_momvement(self):#should be in moved to states
        self.parent.entity.velocity[0] += self.parent.entity.dir[0]*0.02#*abs(math.sin(self.init_time))

    def look_player(self):
        if self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.set_child('Wait_aggro')
        elif abs(self.parent.player_distance[0])<self.parent.entity.attack_distance:
            self.parent.set_child('Attack')

        elif self.parent.player_distance[0] > self.parent.entity.attack_distance or self.parent.player_distance[0] < -self.parent.entity.attack_distance:#far away
            if random.randint(0, 100)==100:
                self.parent.set_child('Jumping')

class Turn_around_aggro():#when the player jumps over, should be a delays before the entity turns around
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.dir[0] = -self.parent.entity.dir[0]

    def update_AI(self):
        self.parent.set_child('Chase')

class Wait_aggro():#the entity should just stay and do nothing for a while
    def __init__(self,parent,duration=70):
        self.parent = parent
        self.duration = duration
        self.parent.entity.currentstate.enter_state('Transform_idle')
        self.velocity = [0,0]

    def update_AI(self):
        self.duration -= 1
        if self.duration < 0:
            self.exit()

    def exit(self):
        if self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.set_child('Turn_around_aggro')#if player jumpt over/under to the other side
        else:
            self.parent.set_child('Chase')

class Attack():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.enter_state('Attack_pre')

    def update_AI(self):
        pass

    def handle_input(self,input):#called when attack animation finished
        if input == 'Attack':#the animation finshed
            self.parent.set_child('Wait_aggro')

class Jumping():
    def __init__(self,parent):
        self.parent = parent
        self.parent.entity.currentstate.enter_state('Jump_pre')
        self.counter = 3#number of times to jump

    def update_AI(self):
        pass

    def handle_input(self,input):#when it finished attack, called when attack animation finished
        if input == 'Landed':#jump animation finsihed
            self.counter -= 1
            if self.counter > 0:
                self.parent.entity.dir[0] = -self.parent.entity.dir[0]
                self.parent.entity.currentstate.enter_state('Jump_pre')
            else:
                self.parent.set_child('Wait_aggro')

class Aggro2(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Angry')

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            else:
                self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0])<self.entity.attack_distance:
            self.entity.currentstate.handle_input('Attack')

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'stage3':
            new_AI = Aggro3(self.entity)
            new_AI.enter_AI()
        elif input == 'jumping':
            new_AI = Jumping(self.entity)
            new_AI.enter_AI()

class Aggro3(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Angry')

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            elif random.randint(0, 100)==99:
                self.entity.currentstate.handle_input('Special_attack')
            else:
                self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0])<self.entity.attack_distance:
            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Rest',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            elif random.randint(0, 100)==99:
                self.entity.currentstate.handle_input('Special_attack')
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'jumping':
            new_AI = Jumping(self.entity)
            new_AI.enter_AI()
