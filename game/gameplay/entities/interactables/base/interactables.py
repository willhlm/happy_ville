from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.states import states_shader
from gameplay.entities.shared.components.hit_component import HitComponent
from gameplay.entities.shared.components.hitstop_component import HitstopComponent

class Interactables(AnimatedEntity):#interactables
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft
        self.shader_state = states_shader.Idle(self)
        self.hit_component = HitComponent(self)
        self.hitstop = HitstopComponent()
        self.flags = {'invincibility': True}

    def update(self, dt):
        super().update(dt)
        self.group_distance()

    def update_render(self, dt):        
        self.shader_state.update_render(dt)

    def draw(self, target):#called just before draw in group
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press T
        pass

    def collision(self, entity):#continiou collision
        pass

    def on_collision(self, entity):#one time collision
        self.shader_state.handle_input('outline')

    def on_noncollision(self, entity):#one time none collision
        self.shader_state.handle_input('idle')   

    def take_hit(self, effect):
        """Delegate to hit component"""      
        return self.hit_component.take_hit(effect)

    def take_dmg(self, damage):#called from hitcomponent
        pass

    def seed_collision(self, seed):#if seed hits
        pass     

    def knock_back(self, amp, dir):#from hit component
        pass

    def emit_particles(self, **kwargs):#from hit component effects
        pass        

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False   