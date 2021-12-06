class Entity_states():
    def __init__(self,entity):
        self.entity=entity
        self.framerate=4
        self.dir=self.entity.dir

    def update_state(self):
        pass

    def enter_state(self):
        self.entity.state_stack.append(self)
        self.entity.frame=0

    def exit_state(self):
        self.entity.state_stack.pop()
        self.entity.frame=0
        self.entity.state=str(type(self.entity.state_stack[-1]).__name__)

    def update_animation(self):
        objname=str(type(self).__name__)

        self.entity.image = self.entity.sprites.get_image(objname,self.entity.frame//self.framerate,self.dir,self.phase)
        self.entity.frame += 1

        if self.entity.frame == self.entity.sprites.get_frame_number(objname,self.dir,self.phase)*self.framerate:
            self.entity.reset_timer()
            self.increase_phase()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        else:
            self.phase='pre'

class Idle(Entity_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.dashing_cooldown=10
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.state=='jump':
            new_state=Jump_stand(self.entity)
            new_state.enter_state()
        elif self.entity.pressed:
            new_state=Walk(self.entity)
            new_state.enter_state()
        elif self.entity.state=='dash':
            new_state=Dash(self.entity)
            new_state.enter_state()
        if not self.entity.collision_types['bottom']:
            new_state=Fall_stand(self.entity)
            new_state.enter_state()

class Walk(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dashing_cooldown=10
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.state=='jump':
            new_state=Jump_run(self.entity)
            new_state.enter_state()
        elif not self.entity.pressed:#stop walking
            self.exit_state()
        elif self.entity.state=='dash':
            new_state=Dash(self.entity)
            new_state.enter_state()
        if not self.entity.collision_types['bottom']:
            new_state=Fall_run(self.entity)
            new_state.enter_state()

class Jump_stand(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] = -11
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.exit_state()

        if self.entity.state == 'dash':
            new_state = Dash(self.entity)
            new_state.enter_state()

class Jump_run(Jump_stand):
    def __init__(self,entity):
        super().__init__(entity)

class Fall_stand(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.exit_state()
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            new_state=Wall(self.entity)
            new_state.enter_state()
        if self.entity.state=='dash':
            new_state=Dash(self.entity)
            new_state.enter_state()

class Fall_run(Fall_stand):
    def __init__(self,entity):
        super().__init__(entity)

class Wall(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dashing_cooldown=10
        self.phase='main'
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.state=='jump':
            self.entity.velocity[0]=-self.entity.dir[0]*10
            self.entity.friction=[0.2,0]
            new_state=Jump_run(self.entity)
            new_state.enter_state()

        if self.entity.collision_types['bottom']:
            self.entity.friction=[0.2,0]
            self.exit_state()

        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction=[0.2,0]
            new_state=Fall_run(self.entity)
            new_state.enter_state()

class Dash(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[0] = 30*self.entity.dir[0]
        self.entity.spirit -= 10
        self.dir=self.entity.ac_dir.copy()
        self.phase='main'
        self.phase=self.phases[0]

    def update_state(self):
        self.entity.dashing_cooldown-=1
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.entity.velocity[0]+self.entity.ac_dir[0]*0.5

        if abs(self.entity.velocity[0])<10:#max horizontal speed
            self.entity.velocity[0]=self.entity.ac_dir[0]*10

        if self.entity.dashing_cooldown<0 or self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.exit_state()

class Death(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.loot()
        self.kill()
