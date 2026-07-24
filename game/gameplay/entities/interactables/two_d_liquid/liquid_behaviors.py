from gameplay.entities.shared.components.hazard import VoidHazardComponent


class LiquidBehavior:
    def __init__(self, entity):
        self.entity = entity
        self.void_hazard = VoidHazardComponent(entity)

    def update(self):#called when animation is finished in reset_timer
        pass

    def on_enter(self, entity):
        pass

    def on_exit(self, entity):
        pass

class WaterBehavior(LiquidBehavior):
    def __init__(self, entity, **properties):
        super().__init__(entity)
        self.liquid_tint = properties.get('liquid_tint', (0.2, 0.6, 1.0, 0.5) )#need to save it seperatly to colour the particles
        self.entity.shader['liquid_tint'] = self.liquid_tint
        self.entity.shader['darker_color'] = properties.get('darker_color', (0.2, 0.6, 1.0, 0.9))
        self.entity.shader['line_color'] = properties.get('line_color',(0.4, 0.7, 1.0, 1))

class PoisonBehavior(LiquidBehavior):
    def __init__(self, entity, **properties):
        super().__init__(entity)
        self.liquid_tint = properties.get('liquid_tint', (0.2, 1, 0.6, 0.5) )#need to save it seperatly to colour the particles
        self.entity.shader['liquid_tint'] = self.liquid_tint
        self.entity.shader['darker_color'] = properties.get('darker_color', (0.2, 1, 0.6, 0.9))
        self.entity.shader['line_color'] = properties.get('line_color',(0.4, 1, 0.7, 1))        
   
    def on_enter(self, entity):
        self.void_hazard.trigger(entity)

class VerticalPoisonBehavior(PoisonBehavior):
    def __init__(self, entity, **properties):
        super().__init__(entity)
        self.scroll_speed = properties.get('scroll_speed', 1)

    def update(self):
        super().update()
        self.update_pos()

    def update_pos(self):
        self.entity.true_pos[1] -= self.scroll_speed * self.entity.game_objects.game.dt
        self.entity.rect.topleft = self.entity.true_pos
        self.entity.full_hitbox.topleft = self.entity.rect.topleft
        self.entity.set_height_percent(self.entity.height_percent)

    def on_enter(self, entity):#when we kill player
        if entity in self.entity.game_objects.players:
            entity.death_manager.die()
            return

        if hasattr(entity, 'currentstate') and hasattr(entity.currentstate, 'die'):
            entity.currentstate.die()
        else:
            entity.kill()
