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
    def __init__(self, damage=1, knockback = [25, 10], hitstop=10, sound_key = None, particles = {}):
        # Gameplay properties
        self.damage = damage
        self.knockback = knockback
        self.hitstop = hitstop
        self.result = HitResult.CONNECTED  # Default result
        
        # Sound key tuple: ('weapon_type',)
        self.sound_key = sound_key
        self.sound = None  # Resolved dynamically

        self.particles = particles
        self.meta = {}
        
        # Callback dicts - populated by factory functions
        self.defender_callbacks = {}
        self.attacker_callbacks = {}
    
    def copy(self):
        new_effect = HitEffect.__new__(HitEffect)
        new_effect.damage = self.damage
        new_effect.knockback = self.knockback[:]
        new_effect.hitstop = self.hitstop
        new_effect.result = self.result
        new_effect.sound_key = self.sound_key  # Copy key
        new_effect.sound = self.sound  # Copy resolved sound
        new_effect.particles = self.particles
        new_effect.meta = self.meta.copy()
        new_effect.defender_callbacks = self.defender_callbacks.copy()
        new_effect.attacker_callbacks = self.attacker_callbacks.copy()
        return new_effect

# ============================================================================
# DEFAULT CALLBACKS
# ============================================================================

def default_defender_sound(defender, effect, attacker_dir):
    """Play hurt sound"""
    try:
        defender.game_objects.sound.play_sfx(defender.sounds['hurt'][0], vol=0.2)
    except:
        pass

def default_defender_particles(defender, effect, attacker_dir):
    """Spawn hit particles"""
    defender.emit_particles(**effect.particles)

def default_defender_hitstop(defender, effect, attacker_dir):
    """Hitstop with knockback"""
    callback = {'knock_back': {'amp': effect.knockback, 'dir': attacker_dir}}
    defender.apply_hitstop(lifetime=effect.hitstop, call_back=callback)

def default_defender_visual(defender, effect, attacker_dir):
    """Visual feedback (hurt flash)"""
    defender.shader_state.handle_input('Hurt')

def default_attacker_hitstop(projectile, effect, defender):
    """Attacker hitstop"""
    projectile.entity.apply_hitstop(lifetime=effect.hitstop, call_back=None)

def default_attacker_particles(projectile, effect, defender):
    """Clash particles (sword-specific)"""
    projectile.clash_particles(defender.hitbox.center, number_particles=5)

def default_attacker_sound(projectile, effect, defender):
    """Hit sound"""
    projectile.game_objects.sound.play_sfx(effect.sound, vol=0.3)

def default_attacker_sound_dynamic(weapon, effect, defender):
    """Dynamically resolve and play hit sound"""        
    material = getattr(defender, 'material', 'flesh')# Get material from defender (default to 'flesh')        
    sound = weapon.game_objects.sound.get_sfx(*effect.sound_key, material)[0]# Resolve sound: ('sword',) + 'flesh' -> get_sfx('sword', 'flesh')
    weapon.game_objects.sound.play_sfx(sound, vol=0.3)

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================
def create_melee_effect(damage, knockback, hitstop, sound_key, particles):#e.g. aila sword
    """Factory for melee weapons (sword, hammer, etc.)"""
    effect = HitEffect(damage, knockback, hitstop, sound_key, particles)
    
    # Set up defender callbacks (executed on enemy/player getting hit)
    effect.defender_callbacks = {
        'sound': default_defender_sound,
        'particles': default_defender_particles,
        'hitstop': default_defender_hitstop,  # Includes knockback
        'visual': default_defender_visual,
    }
    
    # Set up attacker callbacks (executed on sword wielder)
    effect.attacker_callbacks = {
        'hitstop': default_attacker_hitstop,
        'particles': default_attacker_particles,
        'sound': default_attacker_sound_dynamic,
    }
    
    return effect

def create_projectile_effect(damage, knockback, hitstop, sound_key, particles):
    """Factory for projectiles (no attacker hitstop)"""
    effect = HitEffect(damage, knockback, hitstop, sound_key, particles)
    
    effect.defender_callbacks = {
        'sound': default_defender_sound,
        'particles': default_defender_particles,
        'hitstop': default_defender_hitstop,
        'visual': default_defender_visual,
    }
    
    # Projectiles don't have attacker hitstop
    effect.attacker_callbacks = {
        'particles': default_attacker_particles,
        'sound': default_attacker_sound,
    }
    
    return effect

def create_contact_effect(damage, knockback, hitstop, sound_key, particles):#when enemy collides with player
    """Factory for contact damage (enemy touching player)"""
    effect = HitEffect(damage, knockback, hitstop, sound_key, particles)
    
    # Defender callbacks (player getting hit by contact)
    effect.defender_callbacks = {
        'sound': default_defender_sound,
        'particles': default_defender_particles,
        'hitstop': default_defender_hitstop,
    }
    
    # No attacker callbacks (enemy doesn't get feedback from contact)
    effect.attacker_callbacks = {}
    
    return effect    