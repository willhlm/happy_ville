from engine import constants as C
from gameplay.entities.shared.modifiers import modifier_damage
from gameplay.entities.shared.components.hit_results import HitResult

class HitComponent():
    """Handles hit processing for any entity"""
    
    def __init__(self, entity):
        self.entity = entity
        self.damage_manager = modifier_damage.DamageManager(entity)
        self.invincibility_time = C.invincibility_time_enemy
        
        self.hit_handlers = {
            HitResult.BLOCKED: self.on_blocked,
            HitResult.PARRIED: self.on_parried,
            HitResult.REFLECTED: self.on_reflected,
        }
        self.invincibility = False

    def take_hit(self, effect):
        """Process incoming hit. Returns (damage_applied, modified_effect)"""        
        if self.invincibility: return False, effect# Check invincibility first
        effect.defender = self.entity
        self._activate_invincibility(effect)
        
        # Process through modifiers directly
        for modifier in self.damage_manager._sorted_modifiers:
            modifier.modify_hit(effect)            
            if effect.result != HitResult.CONNECTED:# Stop if hit was cancelled
                self._execute_attacker_feedback(effect)
                self.hit_handlers[effect.result](effect)
                return False, effect
                
        effect = self.entity.take_dmg(effect)#hit is conencted: Apply the damage
        self._execute_defender_feedback(effect)
        self._execute_attacker_feedback(effect)        
        
        return True, effect
    
    def on_blocked(self, effect):
        pass      
        
    def on_parried(self, effect):
        pass

    def on_reflected(self, effect):
        pass

    def _execute_defender_feedback(self, effect):
        """Execute defender callbacks"""
        for callback in effect.defender_callbacks.values():
            callback(effect)
    
    def _execute_attacker_feedback(self, effect):        
        """Execute attacker callbacks"""
        for callback in effect.attacker_callbacks.values():
            callback(effect)        

    def _activate_invincibility(self, effect):
        self.set_invinsibility(True)
        effect.game_objects.timer_manager.start_timer(self.invincibility_time, self._on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while

    def _on_invincibility_timeout(self):
        self.set_invinsibility(False)

    def set_invinsibility(self, state):
        self.invincibility = state

    def set_invinsibility_time(self, time):
        self.invincibility_time = time
