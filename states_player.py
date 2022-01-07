import sys, pygame
from states_entity import Entity_States

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update(self):
        super().update()
        self.increase_spirit()

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_spirit(self):
        self.entity.spirit += 0.1
        self.entity.spirit = min(self.entity.max_spirit,self.entity.spirit)

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.phase='pre'

    def change_state(self,input):
        self.enter_state(input)

    #def pressing(self):
    #    self.pressed=False
    #    keys_pressed=pygame.key.get_pressed()
    #    if keys_pressed[pygame.K_LEFT]:
    #        self.pressed=True
    #    if keys_pressed[pygame.K_RIGHT]:
    #        self.pressed=True

class Idle(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            #self.entity.velocity[1]=0
            self.enter_state('Fall_stand')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='a':
                self.enter_state('Jump_stand')
            elif input[-1]=='left':
                self.entity.dir[0] = -1
                self.enter_state('Walk')
            elif input[-1]=='right':
                self.entity.dir[0] = 1
                self.enter_state('Walk')
            elif input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_stand')
            elif input[-1]=='b':
                self.enter_state(self.entity.equip)
            elif input[-1] == 'k':
                self.enter_state('Counter')
            elif input[-1] == 'up':
                self.entity.dir[1] = 1
            elif input[-1] == 'down':
                self.entity.dir[1] = -1
        elif input[1]:
            if input[-1] == 'up' or input[-1] == 'down':
                self.entity.dir[1] = 0

class Walk(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.entity.velocity[1]=0
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[0]:#press
            if input[-1]=='a':
                self.enter_state('Jump_run')
            elif input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_run')
            elif input[-1] == 'b':
                self.enter_state(self.entity.equip)
            elif input[-1] == 'up':
                self.entity.dir[1] = 1
            elif input[-1] == 'down':
                self.entity.dir[1] = -1
            elif input[-1] == 'right' and self.entity.dir[0] == -1:
                self.entity.dir[0]=1
            elif input[-1] == 'left' and self.entity.dir[0] == 1:
                self.entity.dir[0]=-1
        elif input[1]:#release
            if ((input[-1] == 'right' and self.entity.dir[0] == 1) or (input[-1] == 'left' and self.entity.dir[0] == -1)):
                self.enter_state('Idle')

class Jump_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.jumping()

    def jumping(self):
        if self.entity.velocity[1]>0:
            self.entity.velocity[1] = -11

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_run')
            elif input[-1]=='left':
                self.entity.dir[0] = -1
            elif input[-1]=='right':
                self.entity.dir[0] = 1
            elif input[-1]=='b':
                self.enter_state(self.entity.equip)
        elif input[1]:
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1 :
                self.enter_state('Jump_stand')

class Jump_stand(Jump_run):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_stand')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_stand')
            elif input[-1]=='left':
                self.entity.dir[0] = -1
                self.enter_state('Jump_run')
            elif input[-1]=='right':
                self.entity.dir[0] = 1
                self.enter_state('Jump_run')
            elif input[-1]=='b':
                self.enter_state(self.entity.equip)
        elif input[1]:
            if input[-1] == 'right' or input[-1] == 'left':
                self.enter_state('Jump_stand')

class Fall_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.initial_phase()

    def initial_phase(self):
        if self.entity.velocity[1]>6:
            self.phases=['main']
        else:
            self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Walk')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='b':
                self.enter_state(self.entity.equip)
            elif input[-1] == 'right' and self.entity.dir[0]==-1 or input[-1] == 'left' and self.entity.dir[0]==1:
                self.entity.dir[0]=-self.entity.dir[0]

        elif input[1]:
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1 :
                self.enter_state('Fall_stand')

class Fall_stand(Fall_run):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input[0]:#press
            if input[-1]=='left':
                self.entity.dir[0] = -1
                self.enter_state('Fall_run')
            elif input[-1]=='right':
                self.entity.dir[0] = 1
                self.enter_state('Fall_run')
            elif input[-1]=='b':
                self.enter_state(self.entity.equip)
        elif input[1]:
            if input[-1]=='right' or input[-1]=='left':
                pass

class Wall(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.entity.friction[1] = 0.4
        self.next_state='Fall_stand'

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Walk')
        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='a':
                self.entity.friction[1] = 0
                self.entity.velocity[0] = -self.dir[0]*10
                self.enter_state('Jump_run')
            elif input[-1] == 'right' and self.entity.dir[0]==-1 or input[-1] == 'left' and self.entity.dir[0]==1:
                self.next_state='Fall_run'
        elif input[1]:
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
                self.fall()
                self.enter_state(self.next_state)

    def fall(self):
        self.entity.collision_types['left']=False
        self.entity.collision_types['right']=False
        self.entity.friction[1] = 0

        if self.next_state=='Fall_stand':
            self.entity.dir[0] = self.entity.dir[0]
            #self.entity.velocity[0] = -self.dir[0]*2
        else:
            self.entity.dir[0] = -self.entity.dir[0]
            self.entity.velocity[0] = self.dir[0]*2

class Dash(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.done=False#animation flag
        self.walking()
        self.entity.velocity[0] = 10*self.dir[0]
        self.entity.spirit -= 10

    def walking(self):
        if abs(self.entity.velocity[0])>1:
            self.next_state='Walk'
        else:
            self.next_state='Idle'

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            self.enter_state(self.next_state)
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.enter_state('Wall')

    def handle_input(self,input):
        if input[0]:#press
            if input[-1] == 'right':
                self.entity.dir[0]=1
                self.next_state='Walk'
            elif input[-1] == 'left':
                self.entity.dir[0]=-1
                self.next_state='Walk'
        elif input[1]:#release
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
                self.next_state='Idle'

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Counter(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.dir=self.entity.dir.copy()
        self.phases=['main','post']
        self.phase=self.phases[0]
        self.entity.spirit -= 10
        self.done=False#animation flag

        self.entity.shield.lifetime=10
        self.entity.shield.dir=self.dir
        self.entity.projectiles.add(self.entity.shield)#add sword to group

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def handle_input(self,input):
        pass

    def increase_phase(self):
        self.done=True

class Death(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            #self.entity.loot()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

class Hurt(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False
        self.next_state='Idle'

    def update_animation(self):
        super().update_animation()
        self.entity.image.fill((250,250,250),special_flags=pygame.BLEND_ADD)

    def update_state(self):
        if self.done:
            self.enter_state(self.next_state)

    def increase_phase(self):
        self.done = True

    def handle_input(self,input):
        if input[0]:#press
            if input[-1]=='left':
                self.entity.dir[0]=-1
                self.next_state='Walk'
            elif input[-1]=='right':
                self.entity.dir[0]=1
                self.next_state='Walk'
        elif input[1]:#release
            if input[-1]=='left':
                self.next_state='Idle'
            elif input[-1]=='right':
                self.next_state='Idle'

class Sword(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.sword1=False#flag to check if we shoudl go to next sword attack
        self.done=False#animation flag
        self.sword2=False#flag to check if we shoudl go to third sword attack
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.sword.dir=self.dir#sword direction

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='pre':
            self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

        super().increase_phase()

class Sword_run(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update_state(self):
        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done and self.entity.acceleration[0]==0:
            self.enter_state('Idle')
        elif self.done:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='x':
                self.sword1=True
            elif input[-1]=='left':
                self.entity.dir[0]=-1
                self.walk()
            elif input[-1]=='right':#if press left or right
                self.entity.dir[0]=1
                self.walk()
        elif input[1]:
            if ((input[-1] == 'right' and self.entity.dir[0] == 1) or (input[-1] == 'left' and self.entity.dir[0] == -1)):
                self.stay_still()

class Sword_stand(Sword_run):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done and self.entity.acceleration[0]==0:
            self.enter_state('Idle')
        elif self.done:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input[0]:
            if input[-1]=='left':
                self.entity.dir[0]=-1
                self.walk()
            elif input[-1]=='right':#if press left or right
                self.entity.dir[0]=1
                self.walk()
            elif input[-1]=='x':
                self.sword1=True
        elif input[1]:
            if ((input[-1] == 'right' and self.entity.dir[0] == 1) or (input[-1] == 'left' and self.entity.dir[0] == -1)):
                self.stay_still()

class Sword1_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=15#swrod hitbox duration

    def update_state(self):
    #    self.update_hitbox()
        if self.done and self.sword2:
            self.enter_state('Sword2_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def handle_input(self,input):
        if input[-1]=='x' and input[0]:
            self.sword2=True

class Abillitites(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False#animation flag
        self.dir=self.entity.dir.copy()#animation direction

    def make_abillity(self):
        abilityname=str(type(self).__name__)
        return self.entity.abilities[abilityname](self.entity)#make the ability object

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='charge'
        elif self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='main':
            self.phase='post'

class Hammer(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10

    def handle_input(self,input):
        if input[1]:#release
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                ability=self.make_abillity()
                self.entity.projectiles.add(ability)#add sword to group

class Force(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.spirit -= 10
        ability=self.make_abillity()
        self.entity.projectiles.add(ability)#add sword to group
        self.force_jump()
        self.walking()#check if we were walking are idle before

    def update_state(self):
        if self.done:
            self.enter_state(self.next_state)

    def walking(self):
        if abs(self.entity.velocity[0])>0.8:
            self.walk()
            self.next_state='Walk'
        else:
            self.stay_still()
            self.next_state='Idle'

    def force_jump(self):
        if self.dir[1]<0:
            self.entity.velocity[1]=-10

    def handle_input(self,input):
        if input[0]:
            if input[-1] == 'up':
                self.entity.dir[1] = 1
            elif input[-1] == 'down':
                self.entity.dir[1] = -1
            elif input[-1] == 'right':
                self.entity.dir[0]=1
                self.walk()
                self.next_state='Walk'
            elif input[-1] == 'left':
                self.entity.dir[0]=-1
                self.walk()
                self.next_state='Walk'
        elif input[1]:
            if input[-1] == 'up' or input[-1] == 'down':
                self.entity.dir[1] = 0
            elif input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
                self.stay_still()
                self.next_state='Idle'

class Heal(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def heal(self):
        self.entity.spirit-=20
        self.entity.health+=20

    def handle_input(self,input):
        if input[1]:
            self.done=True

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.heal()
            self.done=True

class Stone(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main','post']
        self.phase=self.phases[0]

        self.entity.spirit -= 10

        self.entity.ability.phase='pre'
        self.entity.ability.action='small'
        self.entity.ability.lifetime=100
        self.entity.ability.velocity=[0,0]
        self.entity.ability.update_hitbox()
        self.entity.projectiles.add(self.entity.ability)#add sword to group

    def handle_input(self,input):
        if input[1]:
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                self.entity.ability.frame=0
                self.entity.ability.phase='main'
                self.entity.ability.velocity[0]=self.entity.ability.charge_velocity#set the velocity
            else:#relasing during pre pahse
                self.done=True
                self.entity.ability.frame=0
                self.entity.ability.phase='main'

class Darksaber(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        ability=self.make_abillity()
        self.entity.projectiles.add(ability)#add sword to group

    def handle_input(self,input):
        pass

class Arrow(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10

    def handle_input(self,input):
        if input[0]:
            pass
        elif input[1]:
            pass

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            ability=self.make_abillity()
            self.entity.projectiles.add(ability)#add sword to group

        elif self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='main':
            self.phase='post'
