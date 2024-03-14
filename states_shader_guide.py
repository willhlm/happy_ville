import sys, math
import constants as C

class Shader_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.shader_state = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def update(self):#called in update loop
        pass

    def draw(self):#called just before draw
        pass

class Idle(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['idle']

    def draw(self):
        pos = (int(self.entity.rect[0]-self.entity.game_objects.camera.scroll[0]),int(self.entity.rect[1]-self.entity.game_objects.camera.scroll[1]))
        self.entity.game_objects.game.display.render(self.entity.image, self.entity.game_objects.game.screen, position = pos, flip = bool(max(self.entity.dir[0],0)), shader = self.entity.shader)#shader render

class Teleport(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0

    def update(self):
        self.time += 0.005*self.entity.game_objects.game.dt
        if self.time >= 1:
            self.enter_state('Transparent')

    def draw(self):
        self.entity.layer1.clear(0,0,0,0)

        self.entity.game_objects.shaders['teleport']['progress'] = self.time
        self.entity.game_objects.game.display.render(self.entity.image, self.entity.layer1, shader = self.entity.game_objects.shaders['teleport'])#shader render

        pos = (int(self.entity.rect[0]-self.entity.game_objects.camera.scroll[0]),int(self.entity.rect[1]-self.entity.game_objects.camera.scroll[1]))
        self.entity.game_objects.game.display.render(self.entity.layer1.texture, self.entity.game_objects.game.screen, position = pos, flip = bool(max(self.entity.dir[0],0)), shader = self.entity.game_objects.shaders['bloom'])#shader render

class Transparent(Shader_states):#guide NPC uses it
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 80#put a number so that it matches the animations

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.entity.give_light()
            self.entity.kill()

    def draw(self):
        self.entity.game_objects.shaders['alpha']['alpha'] = 0
        pos = (int(self.entity.rect[0]-self.entity.game_objects.camera.scroll[0]),int(self.entity.rect[1]-self.entity.game_objects.camera.scroll[1]))
        self.entity.game_objects.game.display.render(self.entity.layer1.texture, self.entity.game_objects.game.screen, position = pos, flip = bool(max(self.entity.dir[0],0)), shader = self.entity.game_objects.shaders['alpha'])#shader render
