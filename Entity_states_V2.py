class Entity_states():
    def __init__(self,entity):
        self.entity=entity
        self.framerate=4
        self.dir=self.entity.dir
        self.states={'Idle':Idle,'Walk':Walk,'Fall_stand':Fall_stand,'Fall_run':Fall_run,'Jump_run':Jump_run,'Jump_stand':Jump_stand,'Wall':Wall,'Dash':Dash,'Sword_stand':Sword_stand,'Sword1_stand':Sword1_stand,'Sword_run':Sword_run}

    def update_state(self):
        self.entity.velocity[1]=self.entity.velocity[1]+self.entity.acceleration[1]-self.entity.velocity[1]*self.entity.friction[1]#gravity
        self.entity.velocity[1]=min(self.entity.velocity[1],7)#set a y max speed

        self.entity.velocity[0]=self.entity.velocity[0]-self.entity.friction[0]*self.entity.velocity[0]#friction

    def enter_state(self,newstate):
        self.entity.currentstate=self.states[newstate](self.entity)
        self.entity.frame=0

    def update_animation(self):
        statename=str(type(self).__name__)

        self.entity.image = self.entity.sprites.get_image(statename,self.entity.frame//self.framerate,self.dir,self.phase)
        self.entity.frame += 1

        if self.entity.frame == self.entity.sprites.get_frame_number(statename,self.dir,self.phase)*self.framerate:
            self.entity.reset_timer()
            self.increase_phase()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        else:
            self.phase='pre'

    def change_state(self,input):
        pass

    def horizontal_velocity(self):
        self.entity.velocity[0]+=self.dir[0]*self.entity.acceleration[0]
        self.entity.velocity[0]=self.dir[0]*min(abs(self.entity.velocity[0]),self.entity.max_vel)#max horizontal speed

class Idle(Entity_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        super().update_state()
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand')

    def change_state(self,input):
        if input=='a':
            self.enter_state('Jump_stand')
        elif input=='Left' or input=='Right':
            self.enter_state('Walk')
        elif input=='lb':
            self.enter_state('Dash')
        elif input=='x':
            self.enter_state('Sword_stand')

class Walk(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        super().update_state()
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_run')

        self.horizontal_velocity()

    def change_state(self,input):
        if input=='a':
            self.enter_state('Jump_run')
        elif input==False:
            self.enter_state('Idle')
        elif input=='lb':
            self.enter_state('Dash')
        elif input=='x':
            self.enter_state('Sword_run')

class Jump_stand(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] = -11
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        super().update_state()

        if self.entity.velocity[1]>0:
            self.enter_state('Fall_stand')

    def change_state(self,input):
        if input=='lb':
            self.enter_state('Dash')
        elif input=='x':
            self.enter_state('Sword_stand')
        elif input=='Left' or input=='Right':
            self.enter_state('Jump_run')

class Jump_run(Jump_stand):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        super().update_state()
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_run')

        self.horizontal_velocity()

    def change_state(self,input):
        if input=='lb':
            self.enter_state('Dash')
        elif input=='x':
            self.enter_state('Sword_run')
        elif input==False:
            self.enter_state('Fall_stand')

class Fall_stand(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        super().update_state()

        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def change_state(self,input):
        if input=='Left' or input=='Right':
            self.enter_state('Fall_run')

class Fall_run(Fall_stand):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        super().update_state()

        self.horizontal_velocity()

        if self.entity.collision_types['bottom']:
            self.enter_state('Walk')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')


    def change_state(self,input):
        if input==False:
            self.enter_state('Fall_stand')

class Wall(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.friction[1]=0.4
        self.entity.lfietime=10

    def update_state(self):
        super().update_state()

        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Idle')

        elif self.entity.collision_types['right'] and self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            self.enter_state('Fall_run')

    def change_state(self,input):
        if input=='a':
            self.entity.friction[1]=0
            self.enter_state('Jump_run')

    #    elif input==False:
    #        self.entity.friction[1]=0
    #        self.enter_state('Fall_stand')

class Dash(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.velocity[0] = 30*self.dir[0]
        self.entity.spirit -= 10
        self.done=False#animation flag

    def update_state(self):
        super().update_state()

        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            self.enter_state('Idle')

        if self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.enter_state('Wall')

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        super().increase_phase()

class Death(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        super().update_state()

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

    def update_state(self):
        super().update_state()
        self.entity.sword.updates(self.entity.hitbox)#make the sword hitbox follow the player

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='pre':
            self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

        super().increase_phase()

class Sword_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update_state(self):
        super().update_state()

        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def change_state(self,input):
        if input=='x':
            self.sword1=True


class Sword1_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=15#swrod hitbox duration

    def update_state(self):
        super().update_state()
        if self.done and self.sword2:
            self.enter_state('Sword2_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def change_state(self,input):
        if input=='x':
            self.sword2=True

class Sword_run(Sword_stand):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        super().update_state()
        self.horizontal_velocity()

        if self.done and self.sword1:
            self.enter_state('Sword1_stand')

        elif self.done:#if animation is done
            self.enter_state('Walk')
