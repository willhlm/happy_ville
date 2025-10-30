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
        self.meta = {}
        
        self.result = HitResult.CONNECTED  # Default result

        # Callback dicts - populated by factory functions
        self.defender_callbacks = {}
        self.attacker_callbacks = {}
    
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
        return new_effect

# ============================================================================
# DEFAULT _execute_defender_feedback and _execute_attacker_feedback
# ============================================================================

def default_defender_sound(effect, defender, **kwargs):
    """Play hurt sound"""
    try:
        defender.game_objects.sound.play_sfx(defender.sounds['hurt'][0], vol=0.2)
    except:
        pass

def default_defender_particles(effect, defender, **kwargs):
    """Spawn hit particles"""
    defender.emit_particles(**effect.particles)

def default_defender_hitstop(effect, defender, **kwargs):
    """Hitstop with knockback"""
    callback = {'knock_back': {'amp': effect.knockback, 'dir': effect.meta['attacker_dir']}}
    defender.apply_hitstop(lifetime=effect.hitstop, call_back=callback)

def default_defender_visual(effect, defender, **kwargs):
    """Visual feedback (hurt flash)"""
    defender.shader_state.handle_input('Hurt')

def default_attacker_hitstop(effect, attacker, defender):
    """Attacker hitstop - works for projectiles AND entities"""    
    entity = getattr(attacker, 'entity', attacker)# If projectile: use .entity; if entity: use itself
    entity.apply_hitstop(lifetime=effect.hitstop, call_back=None)

def default_attacker_particles(effect, projectile, defender):
    """Clash particles (projectile-specific)"""
    projectile.clash_particles(defender.hitbox.center, number_particles=5)

def default_sound_dynamic(effect, projectile, defender):
    """Dynamically resolve and play hit sound"""        
    material = getattr(defender, 'material', 'flesh')
    sound = projectile.game_objects.sound.get_sfx(effect.hit_type, material)[0]
    projectile.game_objects.sound.play_sfx(sound, vol = 1)

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