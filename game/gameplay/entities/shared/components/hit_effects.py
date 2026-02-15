from gameplay.entities.shared.components.hit_results import HitResult

"""
Hit Effects System

Defines:
- HitEffect: Data structure for hit information
- Callback builders: Reusable callback functions
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
        self.attacker_particles = kwargs.get('attacker_particles', {})        
        self.projectile = kwargs.get('projectile', None)
        self.meta = kwargs.get('meta', {})
        
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
        new_effect.hit_type = self.hit_type
        new_effect.particles = self.particles.copy()
        new_effect.meta = self.meta.copy()
        new_effect.defender_callbacks = self.defender_callbacks.copy()
        new_effect.attacker_callbacks = self.attacker_callbacks.copy()
        new_effect.projectile = self.projectile
        new_effect.attacker = self.attacker
        new_effect.defender = None        
        return new_effect

    def append_callback(self, target, callback_type, callback_func):
        """
        Append or replace a callback.
        
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
        
        callback_dict[callback_type] = callback_func

# ============================================================================
# CALLBACK BUILDERS - Reusable functions that return callbacks
# ============================================================================

def knockback_callback(entity, knockback, direction):
    """Returns a knockback callback"""
    return lambda: entity.knock_back(amp=knockback, dir=direction)

def screen_shake_callback(camera, **kwargs):
    """Returns a screen shake callback"""
    return lambda: camera.camera_shake(**kwargs)

def spawn_particles_callback(game_objects, **particle_kwargs):
    """Returns a particle spawn callback"""
    return lambda: game_objects.particles.emit(**particle_kwargs)

def play_sound_callback(sound_manager, sound, volume=1.0):
    """Returns a sound play callback"""
    return lambda: sound_manager.play_sfx(sound, vol=volume)

# ============================================================================
# DEFAULT CALLBACKS - Standard behavior when hits occur
# ============================================================================

def default_defender_sound(effect):
    """Play hurt sound"""
    try:
        effect.defender.game_objects.sound.play_sfx(effect.defender.sounds['hurt'][0], vol=0.2)
    except:
        pass

def default_defender_particles(effect):
    """Spawn hit particles"""
    effect.defender.game_objects.particles.emit(effect.particles['preset'], effect.defender.hitbox.center, effect.particles['n'], **effect.particles['args'])

def default_defender_visual(effect):
    """Visual feedback (hurt flash)"""
    effect.defender.shader_state.handle_input('Hurt')

def default_attacker_particles(effect):
    """Clash particles (projectile-specific)"""
    effect.defender.game_objects.particles.emit(effect.attacker_particles['preset'], effect.defender.hitbox.center, effect.attacker_particles['n'],  **effect.attacker_particles['args'])

def default_sound_dynamic(effect):
    """Dynamically resolve and play hit sound"""        
    material = getattr(effect.defender, 'material', 'flesh')
    sound = effect.defender.game_objects.sound.get_sfx(effect.hit_type, material)[0]
    effect.defender.game_objects.sound.play_sfx(sound, vol=1)

# ============================================================================
# FACTORY FUNCTIONS - Create pre-configured effects
# ============================================================================

def create_melee_effect(**kwargs):
    """Factory for melee weapons (sword, hammer, etc.)"""
    effect = HitEffect(**kwargs)
    
    # Defender callbacks (executed on enemy/player getting hit)
    effect.defender_callbacks = {
        'hitstop': lambda eff: eff.defender.hitstop.start(
            duration=eff.hitstop,
            callback=[
                knockback_callback(eff.defender, eff.knockback, eff.meta['attacker_dir'])
            ]
        ),
        'particles': default_defender_particles,        
        'visual': default_defender_visual,
        'sound': default_defender_sound,
    }
    
    # Attacker callbacks (executed on sword wielder)
    effect.attacker_callbacks = {
        'hitstop': lambda eff: eff.attacker.hitstop.start(
            duration=eff.hitstop,
            callback=[]  # No callbacks, just hitstop
        ),
        'particles': default_attacker_particles,
        'sound': default_sound_dynamic,
    }
    
    return effect

def create_projectile_effect(**kwargs):
    """Factory for projectiles (no attacker hitstop)"""
    effect = HitEffect(**kwargs)
    
    effect.defender_callbacks = {        
        'hitstop': lambda eff: eff.defender.hitstop.start(
            duration=eff.hitstop,
            callback=[
                knockback_callback(eff.defender, eff.knockback, eff.meta['attacker_dir'])
            ]
        ),
        'particles': default_defender_particles,
        'visual': default_defender_visual,
        'sound': default_defender_sound,
    }
    
    # Projectiles don't hitstop the attacker
    effect.attacker_callbacks = {
        'particles': default_attacker_particles,
        'sound': default_sound_dynamic,
    }
    
    return effect

def create_contact_effect(**kwargs):
    """Factory for contact damage (enemy touching player)"""
    effect = HitEffect(**kwargs)
    
    # Defender callbacks (player getting hit by contact)
    effect.defender_callbacks = {
        'hitstop': lambda eff: eff.defender.hitstop.start(
            duration=eff.hitstop,
            callback=[
                knockback_callback(eff.defender, eff.knockback, eff.meta['attacker_dir'])
            ]
        ),
        'sound': default_defender_sound,        
    }
    
    # Attacker callbacks (enemy gets hitstop on contact)
    effect.attacker_callbacks = {
        'hitstop': lambda eff: eff.attacker.hitstop.start(
            duration=eff.hitstop,
            callback = []
        ),
    }
    
    return effect