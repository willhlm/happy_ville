class Entity_states():
    def __init__(self,entity):
        self.entity=entity

    def update(self):
        pass

    def enter_state(self):
        self.state_stack.append(self)

    def exit_state(self):
        self.state_stack.pop()

class Idle(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dashing_cooldown=10

    def update(self):
        if self.entity.state=='jump':
            new_state=Jump()
            new_state.enter_state()
        elif self.entity.state=='walk':
            new_state=Walk()
            new_state.enter_state()
        if self.entity.velocity[1]>0:
            new_state=Fall()
            new_state.enter_state()

class Walk(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dashing_cooldown=10

    def update(self):
        if not self.entity.charging[0]:#accelerate horizontal to direction when not dashing
            self.entity.velocity[0]+=self.entity.dir[0]*self.entity.acceleration[0]
            self.entity.friction[0]=0.2
            if abs(self.entity.velocity[0])>self.entity.max_vel:#max horizontal speed
                self.entity.velocity[0]=self.entity.dir[0]*self.entity.max_vel

        if self.entity.state=='jump':
            new_state=Jump()
            new_state.enter_state()
        elif self.entity.state=='idle':#stop walking
            self.exit_state()
        if self.entity.velocity[1]>0:
            new_state=Fall()
            new_state.enter_state()

class Jump(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1] = 0
        self.entity.velocity[1]=-11

    def update(self):
        if self.entity.velocity[1]>0:
            self.exit_state()

class Fall(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.collision_types['bottom']:
            self.exit_state()
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            new_state=Wall()
            new_state.enter_state()

class Wall(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1]=0.4
        self.dashing_cooldown=10

    def update(self):
        if self.entity.state=='jump':
            self.entity.velocity[0]=-self.entity.dir[0]*10
            new_state=Jump()
            new_state.enter_state()

        if self.entity.collision_types['bottom']:
            self.exit_state()

        elif not self.entity.collision_types['right'] or not self.entity.collision_types['left']:#non wall and not on ground
            new_state=Fall()
            new_state.enter_state()


class Dash(Entity_states):
    def __init__(self,entity):
        super().__init__(entity)
        if self.entity.spirit>=10 and not self.entity.charging[0]:#if we have spirit
            self.entity.velocity[0] = 30*self.entity.dir[0]
            self.entity.spirit -= 10

    def update(self):
        self.entity.dashing_cooldown-=1
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.entity.velocity[0]+self.entity.ac_dir[0]*0.5

        if abs(self.entity.velocity[0])<10:#max horizontal speed
            self.entity.velocity[0]=self.entity.ac_dir[0]*10

        if done:
            self.exit_state()
