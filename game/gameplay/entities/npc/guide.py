from gameplay.entities.npc.base.npc import NPC
from gameplay.entities.visuals.particles import particles

class Guide(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def update(self, dt):
        super().update(dt)
        self.shader_state.update_render(dt)#goes between idle and teleport

    def buisness(self):#enters after conversation
        self.shader_state.enter_state('Teleport')
        self.give_light()
        for i in range(0, 10):#should maybe be the number of abilites Aila can aquire?
            particle = getattr(particles, 'Circle')(self.hitbox.center, self.game_objects, distance=0, lifetime = -1, vel = {'linear':[7,15]}, dir='isotropic', scale=5, colour=[100,200,255,255], state = 'Circle_converge',gradient = 1)
            light = self.game_objects.lights.add_light(particle, colour = [100/255,200/255,255/255,255/255], radius = 20)
            particle.light = light#add light reference
            self.game_objects.cosmetics.add(particle)

    def give_light(self):#called when teleport shader is finished
        self.game_objects.lights.add_light(self.game_objects.player, colour = [200/255,200/255,200/255,200/255])
        self.game_objects.world_state.update_event('guide')

    def draw(self, target):#called in group
        self.shader_state.draw()
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

    def load_sprites(self):
        super().load_sprites('guide')   