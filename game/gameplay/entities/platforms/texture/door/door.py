from gameplay.entities.platforms.texture.gate.gate_1 import Gate_1

class Door(Gate_1):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        #self.sfx = ADDSFXHERE
        self.key = kwarg.get('key', 'None')
        self.shader = None        

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def draw(self, target):
        blit_pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.shader_state.draw(self.image, target, blit_pos)

    def shake(self):
        self.shader_state.handle_input('Hurt', colour = (1,1,1,0))
