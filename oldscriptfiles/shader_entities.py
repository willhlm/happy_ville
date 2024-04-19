import shaders

class Shader_entities():
    def __init__(self,entity):
        self.entity = entity
        self.time = 0
        self.window_size = [640,360]
        self.shader_bg = shaders.Shader((entity.rect[2],entity.rect[3]), self.window_size, (0,0), "shaders/vertex.txt", "shaders/default_frag.txt", entity.image)

    def update_pos(self):#scroll
        pos = [2*self.entity.rect.centerx - self.window_size[0],-2*self.entity.rect.centery + self.window_size[1]]#
        self.shader_bg.update_pos(pos)

    def update(self):
        self.time += 1
        #self.shader_bg.send("tx", [self.time])
        #self.shader_bg.send("ty", [self.time])

    def render(self,image):
        self.shader_bg.render(image)

class Shader_BG():
    def __init__(self,entity,surface):
        self.entity = entity
        self.time = 0
        self.window_size = [640,360]
        self.shader_bg = shaders.Shader(self.window_size, self.window_size, (0,0), "shaders/vertex.txt", "shaders/default_frag.txt",surface)

    def update_pos(self):#scroll
        return
        pos = [2*self.entity.rect.centerx - self.window_size[0],-2*self.entity.rect.centery + self.window_size[1]]#
        self.shader_bg.update_pos(pos)

    def update(self):
        self.time += 1
        #self.shader_bg.send("tx", [self.time])
        #self.shader_bg.send("ty", [self.time])

    def render(self,image):
        self.shader_bg.render(image)
