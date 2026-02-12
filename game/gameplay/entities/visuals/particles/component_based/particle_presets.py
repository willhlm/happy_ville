import random
from .particle_builder import ParticleBuilder
from .effect_components import HomingComponent

def spirit_aura(pos, game_objects, colour):#player dashing use this
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=3, gradient=1, colour=colour)
        .velocity_directional(min_speed=2, max_speed=10, direction='isotropic', angle_spread=[30, 30])
        .wave(frequency=0.1, amplitude=0.5, gravity_scale=0.5)  # tune amplitude/frequency, keep gravity_scale=0.5
        .fade(speed=7)
        .lifetime(frames=40)
        .build()
    )    

def black_burst(pos, game_objects):#player getting hurt
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=3, gradient=0, colour=[0, 0, 0, 255])
        .velocity_directional(
            min_speed=7,
            max_speed=15,
            direction="isotropic",
            angle_spread=[30, 30],
        )
        .fade(speed=7)          # old fade_scale=7
        .lifetime(frames=40)    # old lifetime=40
        .build()
    )

def spirit_wisp(pos, game_objects, colour):#dead boss
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=3, gradient=1, colour=colour)
        # Old: vel={'wave':[0, -1]}
        # We keep a tiny base drift upward, and let wave motion do the wobble.
        .velocity_xy(vx=0, vy=-1)
        .wave(amplitude=0.5, frequency=0.1, gravity_scale=0.5)
        .fade(speed=3)
        .lifetime(frames=70)
        .build()
    )

def converging_soul(pos, game_objects, player):#when exploding an abilty ball
    def on_absorb(p, t):#particle, target
        # emit event
        t.game_objects.signals.emit("particles_absorbed")

        # trigger light burst instead of instantly deleting light
        p.light.updates.append(p.light.expand)
        p.light.updates.append(p.light.fade)
        p.light.updates.append(p.light.lifetime)

        # now kill the particle AFTER the burst starts
        p.kill()

    particle = (
        ParticleBuilder(pos, game_objects)
        .circle(scale=5, gradient=1, colour=[100, 200, 255, 255])
        .velocity_directional(min_speed=7, max_speed=15, direction="isotropic")
        .deceleration(factor=0.001, min_vel=0.03)
        .transition(delay=200, callback=lambda p: p.add_component(
            HomingComponent(p, target=player, start_delay=0)
        ))
        .collision(player, distance=5, callback=on_absorb)
        .build()
    )

    # Attach light
    light = game_objects.lights.add_light(
        particle,
        colour=[100/255, 200/255, 255/255, 255/255],
        radius=20
    )
    particle.light = light

    return particle

#not used
def magic_spark(pos, game_objects, target):
    """Homing magic spark."""
    return (ParticleBuilder(pos, game_objects)
        .spark(scale=1.5, colour=[100, 150, 255, 255])
        .velocity_random(8, 12)
        .homing(target, delay=30)
        .fade(speed=2)
        .lifetime(200)
        .build())

def trailing_projectile(pos, game_objects, target):
    """Projectile with trail."""
    return (ParticleBuilder(pos, game_objects)
        .spark(scale=2, colour=[255, 200, 0, 255])
        .velocity_towards(target, 15)
        .trail(interval=3, radius=2, colour=[255, 150, 0, 128], lifetime=20)
        .lifetime(300)
        .build())

PRESETS = {
    "spirit_aura": spirit_aura,
    "converging_soul": converging_soul,
    "trailing_projectile": trailing_projectile,
    "magic_spark": magic_spark,
    'black_burst': black_burst,
    "spirit_wisp": spirit_wisp,
}



# Option 2: Direct (maximum control)
#particle = Circle(pos, game_objects, radius=5)
#particle.velocity = [7, -8]
#particle.lifetime = 120
#particle.add_component(GravityMotion(particle))
#particle.add_component(FadeComponent(particle))
#particle.add_component(LifetimeComponent(particle))