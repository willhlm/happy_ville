from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.states import states_shader
from gameplay.entities.shared.components.hit_component import HitComponent

class Interactables(AnimatedEntity):#interactables
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft
        self.shader_state = states_shader.Idle(self)
        self.hit_component = HitComponent(self)

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

    def player_collision(self, player):#player collision
        self.shader_state.handle_input('outline')

    def player_noncollision(self):#when player doesn't collide: for grass
        self.shader_state.handle_input('idle')

    def take_hit(self, attacker, effect):
        """Delegate to hit component"""       
        return self.hit_component.take_hit(attacker, effect)

    def take_dmg(self, effect):#when player hits with e.g. sword
        pass

    def seed_collision(self, seed):#if seed hits
        pass

    def modify_hit(self, effects):#called when aila sword hit it
        return effects

    def apply_hitstop(self, lifetime=10, call_back=None):#called when aila sword hit it
        pass

    def emit_particles(self, **kwargs):#called when aila sword hit it
        pass        