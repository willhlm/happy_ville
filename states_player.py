import sys, sound, Entities
from states_entity import Entity_States

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update(self):
        super().update()
        self.increase_spirit()
        self.jumping()

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def enter_condition(self,newstate):
        if newstate=='Dash':
            if self.entity.dash:
                self.enter_state(newstate)
        elif newstate=='Wall':
            if self.entity.wall:
                self.enter_state(newstate)

    def increase_spirit(self):
        self.entity.spirit += 0.1
        self.entity.spirit = min(self.entity.max_spirit,self.entity.spirit)

    def increase_phase(self):
        pass

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def jumping(self):
        self.entity.jump_timer -= 1
        if self.entity.jump_timer > 0:
            self.entity.velocity[1] -= 2

    def handle_movement(self,input):
        value = input[2]
        self.entity.acceleration[0] = abs(value[0])
        self.entity.dir[1] = -value[1]

        if value[0] > 0.2:#x
            self.entity.dir[0] = 1
        elif value[0] < -0.2:#x
            self.entity.dir[0] = -1

        #jumping
        if input[-1] == 'a':
            if input[0]:
                if not self.entity.jumping:# if not jumping already
                    self.entity.jump()
            elif input[1]:
                self.entity.jump_timer = 0
                self.entity.velocity[1] = 0.7*self.entity.velocity[1]

class Idle(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            #self.entity.velocity[1]=0
            self.enter_state('Fall_stand')

    def handle_press_input(self,input):
        if input[-1]=='a':
            self.enter_state('Jump_stand')
        elif input[-1]=='lb':
            self.enter_condition('Dash')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.enter_state(self.entity.equip)
        elif input[-1] == 'rt':
            self.enter_state('Counter')
        elif input == 'Hurt':
            self.enter_state('Hurt')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]!=0:
            self.enter_state('Walk')

    def swing_sword(self):
        if self.entity.dir[1]==0:
            self.enter_state('Sword1_stand')
        elif self.entity.dir[1]>0:
            self.enter_state('Sword_up')

class Walk(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            #self.entity.velocity[1]=0
            self.enter_state('Fall_run')

    def handle_press_input(self,input):
        if input[-1]=='a':
            self.enter_state('Jump_run')
        elif input[-1]=='lb':
            self.enter_condition('Dash')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1] == 'b':
            self.enter_state(self.entity.equip)
        elif input == 'Hurt':
            self.enter_state('Hurt')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Idle')

    def swing_sword(self):
        if abs(self.entity.dir[1])<0.8:
            self.enter_state('Sword_run1')
        elif self.entity.dir[1]>0.8:
            self.enter_state('Sword_up')

class Jump_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        #self.entity.velocity[1] -= 3
        if self.entity.velocity[1] > 0.7:
            self.enter_state('Fall_run')

    def handle_press_input(self,input):
        if input[-1]=='lb':
            self.enter_condition('Dash')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.enter_state(self.entity.equip)

    def handle_release_input(self,input):#when release space
        if input[-1]=='a':
            if self.entity.acceleration[0]!=0:
                self.enter_state('Fall_run')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Jump_stand')

    def swing_sword(self):
        if self.entity.dir[1]>0:
            self.enter_state('Sword_up')
        elif self.entity.dir[1]<0:
            self.enter_state('Sword_down')
        else:#right or left
            self.enter_state('Air_sword1')

class Jump_stand(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        #self.entity.velocity[1] -= 3
        if self.entity.velocity[1] > 0.7:
            self.enter_state('Fall_stand')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]!=0:
            self.enter_state('Jump_run')

    def handle_press_input(self,input):
        if input[-1]=='lb':
            self.enter_condition('Dash')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.enter_state(self.entity.equip)

    def handle_release_input(self,input):#when release space
        if input[-1]=='a':
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand')

    def swing_sword(self):
        if self.entity.dir[1]>0:
            self.enter_state('Sword_up')
        elif self.entity.dir[1]<0:
            self.enter_state('Sword_down')
        else:#right or left
            self.enter_state('Air_sword1')

class Double_jump(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.velocity[1]=-10

#    def handle_movement(self,input):
#        super().handle_movement(input)
        #if self.entity.acceleration[0]==0:
        #    self.enter_state('Jump_stand')
        #elif self.entity.acceleration[0]!=0:
        #    self.enter_state('Jump_run')

    def update_state(self):
        if self.entity.velocity[1]>0:#falling down
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand')
            else:
                self.enter_state('Fall_run')

class Fall_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
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
            self.enter_condition('Wall')

    def handle_press_input(self,input):
        if input[-1]=='b':
            self.enter_state(self.entity.equip)
        elif input[-1]=='lb':
            self.enter_condition('Dash')
        elif input[-1]=='x':
            self.swing_sword()
        elif input=='double_jump':
            self.enter_state('Double_jump')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Fall_stand')

    def swing_sword(self):
        if self.entity.dir[1]>0:
            self.enter_state('Sword_up')
        elif self.entity.dir[1]<0:
            self.enter_state('Sword_down')
        else:#right or left
            self.enter_state('Air_sword1')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase='main'

class Fall_stand(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.initial_phase()

    def initial_phase(self):
        if self.entity.velocity[1]>6:
            self.phases=['main']
        else:
            self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')

    def handle_press_input(self,input):
        if input[-1]=='b':
            self.enter_state(self.entity.equip)
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='lb':
            self.enter_condition('Dash')
        elif input=='double_jump':
            self.enter_state('Double_jump')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]!=0:
            self.enter_state('Fall_run')

    def swing_sword(self):
        if self.entity.dir[1]==1:
            self.enter_state('Sword_up')
        elif self.entity.dir[1]==-1:
            self.enter_state('Sword_down')
        else:#right or left
            self.enter_state('Air_sword1')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase='main'

class Wall(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1] = 0.4

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Walk')

        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            self.enter_state('Fall_run')

    def handle_press_input(self,input):
        if input[-1]=='a':
            self.entity.friction[1] = 0
            self.entity.velocity[0] = -self.dir[0]*10
            self.enter_state('Jump_run')

        elif input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
            self.entity.collision_types['right']=False
            self.entity.collision_types['left']=False
            self.fall()
            self.enter_state('Fall_run')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.fall()
            self.enter_state('Fall_run')

    def fall(self):
        self.entity.friction[1] = 0
        self.entity.velocity[0] = -self.entity.dir[0]*2

class Dash(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.done=False#animation flag
        self.entity.velocity[0] = 20*self.dir[0]
        self.entity.spirit -= 10

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            if self.entity.acceleration[0]==0:
                self.enter_state('Idle')
            else:
                self.enter_state('Walk')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:
            if self.entity.acceleration[0]!=0:
                self.enter_state('Wall')
            else:
                self.enter_state('Idle')

    def handle_press_input(self,input):
        if input[-1]=='x':
            self.enter_state('Dash_attack')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
            self.done=True
        elif self.phase=='post':
            self.done=True

class Dash_attack(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['main','post']
        self.phase=self.phases[0]
        self.done=False

        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.sword.dir[1]=0
        self.entity.sword.dir=self.dir.copy()#sword direction
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            if self.entity.acceleration[0]!=0:
                self.enter_state('Wall')
            else:
                self.enter_state('Idle')

    def increase_phase(self):
        if self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Counter(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.dir=self.entity.dir.copy()
        self.entity.spirit -= 10
        self.done=False#animation flag

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            shield=self.entity.shield(self.entity)
            self.entity.projectiles.add(shield)#add sword to group
        elif self.phase=='main':
            self.done=True

class Death(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phase='pre'
        self.stay_still()
        self.entity.death()
        self.entity.velocity[1]=-3

        if self.entity.velocity[0]<0:
            self.dir[0]=1
        else:
            self.dir[0]=-1

    def increase_phase(self):
        if self.phase=='pre':
            if self.entity.collision_types['bottom']:
                self.phase='main'
            else:
                self.phase='charge'
        elif self.phase=='main':
            self.phase='post'
        elif self.phase == 'charge':
            if self.entity.collision_types['bottom']:
                self.phase='main'

class Invisible(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

class Hurt(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.done=False
        self.next_state='Idle'

    def update_state(self):
        if self.done:
            self.enter_state(self.next_state)

    def increase_phase(self):
        self.done = True

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.next_state='Idle'
        else:
            self.next_state='Walk'

class Spawn(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.health=self.entity.max_health
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

class Sword(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.done=False#animation flag
        self.sword2=False#flag to check if we shoudl go to next sword attack
        self.sword3=False#flag to check if we shoudl go to third sword attack
        self.dir = self.entity.dir.copy()#animation direction
        self.entity.sword.dir=self.dir.copy()#sword direction
        sound.Sound.play_sfx(self.entity.sfx_sword)
        self.slash_speed()

    def slash_speed(self):
        if self.entity.sword.equip=='green':
            self.entity.animation_stack[-1].framerate=3

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='pre':
            self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]

    def enter_state(self,input):
        self.entity.animation_stack[-1].framerate = 4
        super().enter_state(input)

class Sword_run1(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done and self.sword2:
            self.enter_state('Sword_run2')
        elif self.done and self.entity.acceleration[0]==0:
            self.enter_state('Idle')
        elif self.done:
            self.enter_state('Walk')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='x':
            self.sword2=True

class Sword_run2(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done and self.entity.acceleration[0]==0:
            self.enter_state('Idle')
        elif self.done:
            self.enter_state('Walk')

class Sword1_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done and self.sword2:
            self.enter_state('Sword2_stand')
        elif self.done and self.entity.acceleration[0]==0:
            self.enter_state('Idle')
        elif self.done:
            self.enter_state('Walk')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='x':
            self.sword2=True

class Sword2_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done and self.sword3:
            self.enter_state('Sword3_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='x' and input[0]:
            self.sword3=True

class Sword3_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=15#swrod hitbox duration
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done:#if animation is done
            if self.entity.acceleration[0]==0:
                self.enter_state('Idle')
            else:
                self.enter_state('Walk')

class Air_sword2(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=0

    def update_state(self):
        if self.done:
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand')
            else:
                self.enter_state('Fall_run')

class Air_sword1(Air_sword2):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        super().update_state()
        if self.done and self.sword2:
            self.enter_state('Air_sword2')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='x':
            self.sword2=True

class Sword_up(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=10

    def update_state(self):
        if self.done:
            if self.entity.acceleration[0]==0:
                self.enter_state('Idle')
            else:
                self.enter_state('Walk')

class Sword_down(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def update_state(self):
        if self.done:
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand')
            else:
                self.enter_state('Fall_run')

class Plant_bone(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

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

class Thunder(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.aura=Entities.Thunder_aura(self.entity)
        self.entity.game_objects.cosmetics.add(self.aura)
        self.phases=['pre','charge','main']
        self.phase=self.phases[0]

    def update_state(self):
        super().update_state()
        self.entity.spirit -= 0.5
        self.aura.update_hitbox()

    def handle_movement(self,input):
        pass

    def attack(self):
        self.aura.state='post'
        self.aura.animation.reset_timer()

        collision_ene = self.entity.game_objects.collisions.thunder_attack(self.aura)
        if collision_ene:
            for enemy in collision_ene:
                ability=self.entity.abilities['Thunder'](self.entity,enemy.rect)
                self.entity.projectiles.add(ability)#add attack to group

    def handle_release_input(self,input):
        if input[-1]=='b':#when release the botton
            self.attack()

            if self.phase=='charge':
                self.phase='main'
                self.entity.animation_stack[-1].reset_timer()

            elif self.phase=='pre':
                self.enter_state('Idle')

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

    def handle_press_input(self,input):
        if input[-1] == 'right' or input[-1] == 'left':
            self.walk()
            self.next_state='Walk'

    def handle_release_input(self,input):
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

    def handle_press_input(self,input):
        super().handle_press_input(input)
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

    def handle_release_input(self,input):

        if input[-1]=='b' and self.phase=='charge':#when release the botton
            self.phase='main'
            self.entity.animation_stack[-1].reset_timer()
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

class Arrow(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            ability=self.make_abillity()
            self.entity.projectiles.add(ability)#add sword to group

        elif self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='main':
            self.phase='post'
