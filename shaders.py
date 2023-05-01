import moderngl
import pygame
import numpy as np
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

ctx = None

def clear(color):
    ctx.clear(color=(color[0]/255, color[1]/255, color[2]/255))

def create_shader(vertex_filepath, fragment_filepath, ctx):
    with open(vertex_filepath,'r') as f:
        vertex_src = f.read()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.read()

    shader = ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)

    return shader

class Shader:
    def __init__(self, size, display, pos, vertex_path, fragment_path, target_texture=None):
        global ctx
        if ctx is None:
            ctx = moderngl.create_context()

        self.ctx = ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA

        self.shader_data = {}
        self.shader = create_shader(vertex_path, fragment_path, self.ctx)
        self.render_rect = ScreenRect(size, display, pos, self.ctx, self.shader)

        if target_texture is not None:
            s = pygame.Surface(target_texture.get_size())
            self.screen_texture = Texture(s, self.ctx)

    def update_pos(self,pos):
        self.render_rect.update_pos(pos)

    def send(self, name, data):
        if name in self.shader_data:
            if [float(x) for x in data] == self.shader_data[name]:
                return
        self.shader_data[name] = [float(x) for x in data]

    def render(self, surface=None):
        if surface is not None:
            self.screen_texture.update(surface)
            self.screen_texture.use()

        for key in self.shader_data.keys():
            data = self.shader_data[key]
            if len(data) == 1:
                self.shader[key].value = data[0]

            elif len(data) == 2:
                self.shader[key].value = (data[0], data[1])

        self.render_rect.vao.render()

class ScreenRect:
    def __init__(self, size, win_size, offset, ctx, program):
        self.size = size
        offset = (offset[0]/win_size[0], offset[1]/win_size[1])

        self.current_w, self.current_h = win_size

        self.x = self.size[0] / win_size[0]
        self.y = self.size[1] / win_size[1]

        self.vertices = [
            (-self.x + offset[0],  self.y + offset[1]),
             (self.x + offset[0],  self.y + offset[1]),
            (-self.x + offset[0], -self.y + offset[1]),

           (-self.x + offset[0], -self.y + offset[1]),
           (self.x + offset[0],  self.y + offset[1]),
           (self.x + offset[0], -self.y + offset[1]),
        ]
        self.tex_coords = [
           (0.0, 1.0),
           (1.0, 1.0),
           (0.0, 0.0),

           (0.0, 0.0),
           (1.0, 1.0),
           (1.0, 0.0),
        ]

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.tex_coords = np.array(self.tex_coords, dtype=np.float32)
        self.data = np.hstack([self.vertices, self.tex_coords])

        self.vertex_count = 6

        self.vbo = ctx.buffer(self.data)

        try:
            self.vao = ctx.vertex_array(program, [(self.vbo, '2f 2f', 'vertexPos', 'vertexTexCoord'),])
        except moderngl.error.Error:
            self.vbo = ctx.buffer(self.vertices)
            self.vao = ctx.vertex_array(program, [(self.vbo, '2f', 'vertexPos'),])

        self.program = program

    def update_pos(self,offset):
        offset = (offset[0]/self.current_w, offset[1]/self.current_h)

        self.data[:,0:2] = [
            (-self.x + offset[0],  self.y + offset[1]),
             (self.x + offset[0],  self.y + offset[1]),
            (-self.x + offset[0], -self.y + offset[1]),

           (-self.x + offset[0], -self.y + offset[1]),
           (self.x + offset[0],  self.y + offset[1]),
           (self.x + offset[0], -self.y + offset[1]),
        ]

        self.vbo.write(self.data)# update the buffer

class Texture:
    def __init__(self, surface, ctx):
        image = surface
        image = pygame.transform.flip(image, False, True)
        image_width,image_height = image.get_rect().size
        img_data = pygame.image.tostring(image,'RGBA')
        self.texture = ctx.texture(size=image.get_size(), components=4, data=img_data)
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

    def update(self, image):
        image = pygame.transform.flip(image, False, True)
        image_width,image_height = image.get_rect().size
        img_data = pygame.image.tostring(image,'RGBA')

        self.texture.write(img_data)

    def use(self):
        self.texture.use()
