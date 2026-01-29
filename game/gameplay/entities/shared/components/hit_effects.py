from gameplay.entities.shared.components.hit_results import HitResult

"""
Hit Effects System

Defines:
- HitEffect: Data structure for hit information
- Default callbacks: Standard behavior when hits occur
- Factory functions: Create pre-configured effects
"""

class HitEffect():
    """Represents a hit with all its properties"""
    def __init__(self, **kwargs):
        # Gameplay properties
        self.damage = kwargs.get('damage', 1)
        self.knockback = kwargs.get('knockback', [25, 10])
        self.hitstop = kwargs.get('hitstop', 10)                        
        self.hit_type = kwargs.get('hit_type', 'sword')
        self.particles = kwargs.get('particles', {})        
        self.projectile = kwargs.get('projectile', None)
        self.meta = {}
        
        self.result = HitResult.CONNECTED  # Default result

        # Callback dicts - populated by factory functions
        self.defender_callbacks = {}
        self.attacker_callbacks = {}

        # Runtime context (set at collision time)
        self.attacker = kwargs.get('attacker', None)
        self.defender = None        
    
    def copy(self):
        new_effect = HitEffect.__new__(HitEffect)
        new_effect.damage = self.damage
        new_effect.knockback = self.knockback[:]
        new_effect.hitstop = self.hitstop
        new_effect.result = self.result
        new_effect.hit_type = self.hit_type  # Copy key
        new_effect.particles = self.particles
        new_effect.meta = self.meta.copy()
        new_effect.defender_callbacks = self.defender_callbacks.copy()
        new_effect.attacker_callbacks = self.attacker_callbacks.copy()
        new_effect.projectile = self.projectile
        new_effect.attacker = self.attacker
        new_effect.defender = None        
        return new_effect

    def append_callback(self, target, callback_type, callback_func):
        """
        Append or replace a callback with optional arguments.
        
        Args:
            target: 'attacker' or 'defender'
            callback_type: String key for the callback (e.g., 'hitstop', 'sound')
            callback_func: The callback function to register
        
        Example:
            effect.append_callback('defender', 'hitstop', custom_hitstop)
            effect.append_callback('attacker', 'sound', custom_sound)
        """
        if target == 'defender':
            callback_dict = self.defender_callbacks
        elif target == 'attacker':
            callback_dict = self.attacker_callbacks
        
        # If no kwargs, store the function directly (backward compatible)
        callback_dict[callback_type] = callback_func

# ============================================================================
# DEFAULT _execute_defender_feedback and _execute_attacker_feedback
# ============================================================================

def default_defender_sound(effect):
    """Play hurt sound"""
    try:
        effect.defender.game_objects.sound.play_sfx(effect.defender.sounds['hurt'][0], vol=0.2)
    except:
        pass

def default_defender_particles(effect):
    """Spawn hit particles"""
    effect.defender.emit_particles(**effect.particles)

def default_defender_hitstop(effect):
    """Hitstop with knockback"""
    callback = {'knock_back': {'amp': effect.knockback, 'dir': effect.meta['attacker_dir']}}
    effect.defender.apply_hitstop(lifetime=effect.hitstop, call_back=callback)

def default_defender_visual(effect):
    """Visual feedback (hurt flash)"""
    effect.defender.shader_state.handle_input('Hurt')

def default_attacker_hitstop(effect):
    """Attacker hitstop - works for projectiles AND entities"""    
    #entity = getattr(effect.attacker, 'entity', effect.attacker)# If projectile: use .entity; if entity: use itself
    effect.attacker.apply_hitstop(lifetime=effect.hitstop, call_back=None)

def default_attacker_particles(effect):
    """Clash particles (projectile-specific)"""
    effect.projectile.clash_particles(effect.defender.hitbox.center, number_particles=5)

def default_sound_dynamic(effect):
    """Dynamically resolve and play hit sound"""        
    material = getattr(effect.defender, 'material', 'flesh')
    sound = effect.attacker.game_objects.sound.get_sfx(effect.hit_type, material)[0]
    effect.attacker.game_objects.sound.play_sfx(sound, vol = 1)

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================
def create_melee_effect(**kwargs):#e.g. aila sword
    """Factory for melee weapons (sword, hammer, etc.)"""
    effect = HitEffect(**kwargs)
    
    # Set up defender callbacks (executed on enemy/player getting hit)
    effect.defender_callbacks = {
        'hitstop': default_defender_hitstop,  # Includes knockback
        'particles': default_defender_particles,        
        'visual': default_defender_visual,
        'sound': default_defender_sound,
    }
    
    # Set up attacker callbacks (executed on sword wielder)
    effect.attacker_callbacks = {
        'hitstop': default_attacker_hitstop,#without knock back
        'particles': default_attacker_particles,
        'sound': default_sound_dynamic,
    }
    
    return effect

def create_projectile_effect(**kwargs):
    """Factory for projectiles (no attacker hitstop)"""
    effect = HitEffect(**kwargs)
    
    effect.defender_callbacks = {        
        'hitstop': default_defender_hitstop,  # Includes knockback
        'particles': default_defender_particles,
        'visual': default_defender_visual,
        'sound': default_defender_sound,
    }
    
    # Projectiles don't have attacker hitstop
    effect.attacker_callbacks = {
        'hitstop': default_attacker_hitstop,#without knock back
        'particles': default_attacker_particles,
        'sound': default_sound_dynamic,
    }
    
    return effect

def create_contact_effect(**kwargs):#when enemy collides with player
    """Factory for contact damage (enemy touching player)"""
    effect = HitEffect(**kwargs)
    
    # Defender callbacks (player getting hit by contact)
    effect.defender_callbacks = {
        'hitstop': default_defender_hitstop,        
        'sound': default_defender_sound,        
    }
    
    # No attacker callbacks (enemy doesn't get feedback from contact)
    effect.attacker_callbacks = {
        'hitstop': default_attacker_hitstop,
    }
    
    return effect    