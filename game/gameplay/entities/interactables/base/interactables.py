from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager
from gameplay.entities.shared.components.hit_component import HitComponent
from gameplay.entities.base.animated_entity import AnimatedEntity

class Interactables(AnimatedEntity):#interactables
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft

        self.shader_state = EntityShaderManager(self)
        self.hit_component = HitComponent(self)

    def update(self, dt):
        super().update(dt)
        self.group_distance()        

    def update_render(self, dt):        
        self.shader_state.update_render(dt)

    def draw(self, target):
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.shader_state.draw(self.image, target, self.blit_pos, flip = self.dir[0] > 0)

    def on_collision(self, entity):#one time collision
        self.shader_state.add_shader('outline')
        
    def on_noncollision(self, entity):#one time none collision
        self.shader_state.remove_shader('outline')

    def take_hit(self, effect):
        """Delegate to hit component"""      
        effect.defender_callbacks.pop('particles', None)
        effect.defender_callbacks.pop('hitstop', None)
        effect.attacker_callbacks.pop('sword_jump', None)
        effect.attacker_callbacks.pop('hitstop', None)
        effect.attacker_callbacks.pop('sword_jump', None)
        return self.hit_component.take_hit(effect)

    def take_dmg(self, effect):
        return effect

    def interact(self):#when player press T
        pass

    def collision(self, entity):#continiou collision
        pass

    def seed_collision(self, seed):#if seed hits
        pass     
