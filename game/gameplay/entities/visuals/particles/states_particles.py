import sys, random, math

def sign(num):
    if num < 0: return -1
    return 1

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        pass

    def update_render(self, dt):
        pass

    def handle_input(self, input):
        pass

class Idle(Basic_states):#the normal particles
    def __init__(self,entity):
        super().__init__(entity)

    def update_render(self, dt):
        self.entity.set_velocity(dt)
        self.entity.fading(dt)
        self.entity.destroy()

class Circle_converge(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 200#the time when they shoudl converge to aila
        self.sign = [sign(self.entity.velocity[0]),sign(self.entity.velocity[1])]

    def update_render(self, dt):
        self.time -= dt
        self.update_velocity(dt)
        if self.time < 0:
            self.enter_state('Circle_converge_2')

    def update_velocity(self, dt):
        distance = ((self.entity.true_pos[0] - self.entity.spawn_point[0])**2+(self.entity.true_pos[1] - self.entity.spawn_point[1])**2)**0.5

        self.entity.velocity[0] -=  0.001*distance*self.entity.velocity[0]*dt#0.1*math.cos(self.angle)
        self.entity.velocity[1] -= 0.001*distance*self.entity.velocity[1]*dt#0.1*math.sin(self.angle)
        self.entity.velocity[0] = self.sign[0] * max(abs(self.entity.velocity[0]),0.03)#so that it keeps moving a bit
        self.entity.velocity[1] = self.sign[1] * max(abs(self.entity.velocity[1]),0.03)#so that it keeps moving a bit

class Circle_converge_2(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_render(self, dt):     
        self.update_velocity(dt)
        self.check_collision()

    def check_collision(self):
        distance = ((self.entity.true_pos[0] - self.entity.game_objects.player.hitbox.center[0])**2+(self.entity.true_pos[1] - self.entity.game_objects.player.hitbox.center[1])**2)**0.5
        if distance < 5:#light up the room brifly
            self.entity.light.colour = [1,1,1,1]#change the colour of the light
            self.entity.light.updates.append(self.entity.light.expand)
            self.entity.light.updates.append(self.entity.light.fade)
            self.entity.light.updates.append(self.entity.light.lifetime)
            self.entity.kill()

    def update_velocity(self, dt):
        x = self.entity.true_pos[0] - self.entity.game_objects.player.hitbox.center[0]
        y = self.entity.true_pos[1] - self.entity.game_objects.player.hitbox.center[1]

        self.sign = [sign(x),sign(y)]

        angle = math.atan(y/x)
        self.entity.velocity[0] = -self.sign[0]*abs(math.cos(angle))*dt* min(max(abs(x),2),20)
        self.entity.velocity[1] = -self.sign[1]*abs(math.sin(angle))*dt * min(max(abs(y),2),20)