import sys, random, math

def sign(num):
    if num < 0: return -1
    return 1

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.state = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        pass

    def handle_input(self,input):
        pass

class Idle(Basic_states):#the normal particles
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.update_velocity()
        self.entity.fading()
        self.entity.destroy()

class Circle_converge(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 200#the time when they shoudl converge to aila
        self.sign = [sign(self.entity.velocity[0]),sign(self.entity.velocity[1])]

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        self.update_velocity()
        if self.time < 0:
            self.enter_state('Circle_converge_2')

    def update_velocity(self):
        distance = ((self.entity.true_pos[0] - self.entity.spawn_point[0])**2+(self.entity.true_pos[1] - self.entity.spawn_point[1])**2)**0.5

        self.entity.velocity[0] -=  0.001*distance*self.entity.velocity[0]*self.entity.game_objects.game.dt#0.1*math.cos(self.angle)
        self.entity.velocity[1] -= 0.001*distance*self.entity.velocity[1]*self.entity.game_objects.game.dt#0.1*math.sin(self.angle)
        self.entity.velocity[0] = self.sign[0] * max(abs(self.entity.velocity[0]),0.03)#so that it keeps moving a bit
        self.entity.velocity[1] = self.sign[1] * max(abs(self.entity.velocity[1]),0.03)#so that it keeps moving a bit

class Circle_converge_2(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.update_velocity()
        self.check_collision()

    def check_collision(self):
        distance = ((self.entity.true_pos[0] - self.entity.game_objects.player.hitbox.center[0])**2+(self.entity.true_pos[1] - self.entity.game_objects.player.hitbox.center[1])**2)**0.5
        if distance < 5:#light up the room brifly -> make also aila glow blue maybe
            if not self.entity.game_objects.shader_draw.shaders.get('bloom',False):#do not append several if already exist
                self.entity.game_objects.shader_draw.append_shader('bloom', targetColor = [0.39, 0.78, 1], colorRange = 0.2)#append a bloom shader to screen -> should each particle add this?
                self.entity.game_objects.player.shader_state.enter_state('Shining')
            self.entity.light.colour = [1,1,1,1]#change the colour of the light
            self.entity.light.updates.append(self.entity.light.expand)
            self.entity.light.updates.append(self.entity.light.fade)
            self.entity.light.updates.append(self.entity.light.lifetime)
            self.entity.kill()

    def update_velocity(self):
        self.sign = [sign(self.entity.true_pos[0] - self.entity.game_objects.player.hitbox.center[0]),sign(self.entity.true_pos[1] - self.entity.game_objects.player.hitbox.center[1])]

        x = self.entity.true_pos[0] - self.entity.game_objects.player.hitbox.center[0]
        y = self.entity.true_pos[1] - self.entity.game_objects.player.hitbox.center[1]

        angle = math.atan(y/x)
        self.entity.velocity[0] -= 0.1*self.sign[0]*abs(math.cos(angle))*self.entity.game_objects.game.dt
        self.entity.velocity[1] -= 0.1*self.sign[1]*abs(math.sin(angle))*self.entity.game_objects.game.dt

    def handle_input(self,input):
        if input == 'light_gone':#called from lights when lifetime < 0
            if self.entity.game_objects.shader_draw.shaders.get('bloom',False):#do not append several if already exist
                self.entity.game_objects.shader_draw.remove_shader('bloom')
                self.entity.game_objects.player.shader_state.enter_state('Idle')
