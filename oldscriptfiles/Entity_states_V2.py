class Entity_states():
    def __init__(self,entity):
        self.entity=entity
        self.framerate=4
        self.frame=0
        self.dir=self.entity.dir
        self.states={'Idle':Idle,'Walk':Walk,'Fall_stand':Fall_stand,'Fall_run':Fall_run,'Jump_run':Jump_run,'Jump_stand':Jump_stand,'Wall':Wall,'Dash':Dash,'Sword_stand':Sword_stand,'Sword1_stand':Sword1_stand,'Sword_run':Sword_run,'Hammer':Hammer}

    def update(self):
        self.update_velocities()
        self.update_state()

    def update_velocities(self):
        self.entity.velocity[1]=self.entity.velocity[1]+self.entity.acceleration[1]-self.entity.velocity[1]*self.entity.friction[1]#gravity
        self.entity.velocity[1]=min(self.entity.velocity[1],7)#set a y max speed

        self.entity.velocity[0]+=self.dir[0]*self.entity.acceleration[0]
        self.entity.velocity[0]=self.dir[0]*min(abs(self.entity.velocity[0]),self.entity.max_vel)#max horizontal speed
        self.entity.velocity[0]=self.entity.velocity[0]-self.entity.friction[0]*self.entity.velocity[0]#friction

    def enter_state(self,newstate):
        self.entity.currentstate=self.states[newstate](self.entity)
        print(self.entity.currentstate)

    def handle_input(self,input):
        pass

    def update_animation(self):
        statename=str(type(self).__name__)

        self.entity.image = self.entity.sprites.get_image(statename,self.frame//self.framerate,self.dir,self.phase)
        self.frame += 1

        if self.frame == self.entity.sprites.get_frame_number(statename,self.dir,self.phase)*self.framerate:
            self.reset_timer()
            self.increase_phase()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.phase='pre'

    def reset_timer(self):
        self.frame=0

class Idle(Entity_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand')

    def handle_input(self,input):
        if input[-1]=='a':
            self.enter_state('Jump_stand')
        elif input[-1]=='left' and input[0]:
            self.entity.dir[0] = -1
            self.enter_state('Walk')
        elif input[-1]=='right' and input[0]:
            self.entity.dir[0] = 1
            self.enter_state('Walk')
        elif input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_stand')
        elif input[-1]=='e':
            self.enter_state(self.entity.equip)

    def horizontal_velocity(self):
        pass

class Walk(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[-1]=='a':
            self.enter_state('Jump_run')
        elif input[1] and ((input[-1] == 'right' and self.entity.dir[0] == 1) or (input[-1] == 'left' and self.entity.dir[0] == -1)):
            self.enter_state('Idle')
        elif input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_run')

class Jump_run(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] = -11
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_run')
        elif input[-1]==False:
            self.enter_state('Fall_stand')

class Jump_stand(Jump_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_stand')

    def handle_input(self,input):
        if input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_stand')
        elif input[-1]=='Left' or input[-1]=='Right':
            self.enter_state('Jump_run')

    def horizontal_velocity(self):
        pass

class Fall_run(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Walk')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def handle_input(self,input):
        if input==False:
            self.enter_state('Fall_stand')

class Fall_stand(Fall_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def handle_input(self,input):
        if input[-1]=='Left' or input[-1]=='Right':
            self.enter_state('Fall_run')

    def horizontal_velocity(self):
        pass

class Wall(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.friction[1]=0.4
        self.entity.lfietime=10

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Idle')

        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            self.enter_state('Fall_run')

    def handle_input(self,input):
        if input[-1]=='a':
            self.entity.friction[1]=0
            self.enter_state('Jump_run')

    #    elif input==False:
    #        self.entity.friction[1]=0
    #        self.enter_state('Fall_stand')

class Dash(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.entity.spirit -= 10
        self.done=False#animation flag
        self.entity.velocity[0] = 30*self.dir[0]

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.enter_state('Wall')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Death(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.loot()
        self.kill()

class Sword(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.sword1=False#flag to check if we shoudl go to next sword attack
        self.done=False#animation flag
        self.sword2=False#flag to check if we shoudl go to third sword attack
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.sword.dir=self.dir#sword direction

    def update_hitbox(self):
        self.entity.sword.updates(self.entity.hitbox)#make the sword hitbox follow the player

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='pre':
            self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

        super().increase_phase()

class Sword_run(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update_state(self):
        self.update_hitbox()

        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done:#if animation is done
            self.enter_state('Walk')

    def handle_input(self,input):
        if input[-1]=='x':
            self.sword1=True

class Sword_stand(Sword_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.update_hitbox()

        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def horizontal_velocity(self):
        pass

class Sword1_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=15#swrod hitbox duration

    def update_state(self):
        self.update_hitbox()
        if self.done and self.sword2:
            self.enter_state('Sword2_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def handle_input(self,input):
        if input[-1]=='x':
            self.sword2=True

    def horizontal_velocity(self):
        pass

class Abillitites(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.done=False#animation flag
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='charge'
        elif self.phase=='main':
            self.done=True

    def horizontal_velocity(self):
        pass

class Hammer(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main']
        self.phase=self.phases[0]
        self.entity.hammer.dir=self.dir#sword direction
        self.entity.spirit -= 10
        self.entity.hammer.lifetime=7

    def update_state(self):
        if self.phase=='main':
            self.entity.hammer.updates(self.entity.hitbox)#make the sword hitbox follow the player
        if self.done:
            self.entity.hammer.kill()
            self.enter_state('Idle')

    def handle_input(self,input):
        if input[-1]==True and self.phase=='charge':#when release the botton
            self.phase='main'
            self.reset_timer()
            self.entity.projectiles.add(self.entity.hammer)#add sword to group
        else:#relasing during pre pahse
            self.entity.hammer.kill()
            self.enter_state('Idle')
