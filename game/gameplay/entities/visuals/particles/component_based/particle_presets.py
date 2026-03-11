import random, math
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

def burst(pos, game_objects, colour):#player getting hurt
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=3, gradient=0, colour=colour)
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

def converging_soul(pos, game_objects, player):#when exploding an abilty ball, guide
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

def sword_hit(pos, game_objects, *, dir, colour):#entities getting hurt by sword
    # Old:
    # lifetime=180, scale=5, gradient=1, colour=C.spirit_colour
    # vel={'ejac':[13,17]}, angle_spread=[13,15], angle_dist='normal'
    # gravity_scale=-0.1, fade_scale=2.2
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=5, gradient=1, colour=colour)
        .velocity_directional(
            min_speed=13, max_speed=17,
            direction=dir,
            angle_spread=[13, 15],
            angle_dist="normal",
        )
        .ejac()                 # matches old vel={'ejac':...}
        .gravity(scale=-0.1)    # old gravity_scale
        .fade(speed=2.2)        # old fade_scale
        .lifetime(frames=180)   # old lifetime
        .build()
    )

def sword_clash(pos, game_objects, *, angle, colour):#aila's sword clash particles
    # Old:
    # type='Spark', lifetime=10, vel={'linear':[5,7]}, dir=angle (random),
    # scale=0.8, fade_scale=7
    return (
        ParticleBuilder(pos, game_objects)
        .spark(scale=0.8, colour=colour)
        .velocity_directional(
            min_speed=5, max_speed=7,
            direction=angle,
            angle_spread=[0, 0],     # keep it on that exact angle (old behavior)
            angle_dist=None
        )
        # no .ejac() because old was linear motion
        .fade(speed=7)
        .lifetime(frames=10)
        .build()
    )

def spark_scatter(pos, game_objects, *, distance=100, colour=(255,255,255,255)):#soul essence
    # spawn in a ring/disk around pos
    a = random.uniform(0, 2 * math.pi)
    r = distance * math.sqrt(random.random())  # disk; use r=distance for ring
    spawn_pos = (pos[0] + r * math.cos(a), pos[1] + r * math.sin(a))

    return (
        ParticleBuilder(spawn_pos, game_objects)
        .spark(colour=list(colour))
        .homing(target=pos, delay=0, speed_min=2, speed_max=4)  # <-- inward motion
        .fade(speed=10)
        .lifetime(frames=20)
        .build()
    )

def circle_wave(pos, game_objects, *, distance=30, colour=(255,255,255,255)):#cavegrass
    # spawn around the center (uniform disk)
    a = random.uniform(0, 2 * math.pi)
    value = random.uniform(0.5, 1)
    r = distance * math.sqrt(random.random())
    spawn_pos = (pos[0] + r * math.cos(a), pos[1] + r * math.sin(a))

    return (
        ParticleBuilder(spawn_pos, game_objects)
        .circle(scale=2, gradient = 1, colour=list(colour))
        .wave(gravity_scale=1, frequency = 0.1 * value, amplitude=1)   # old vel={'wave':[3,14]}
        .fade(speed=1.5)
        .lifetime(frames=300)
        .build()
    )

def tiny_trail(pos, game_objects, *, dir, vx, vy, colour=(255,255,255,255)):#arrow
    # Old: vel={'linear':[vx*0.1, vy*0.1]}
    # Interpret as "speed proportional to current velocity"
    speed = 0.1 * math.sqrt(vx*vx + vy*vy)

    # Keep it visible even when nearly stopped
    min_speed = max(0.2, speed * 0.8)
    max_speed = max(min_speed, speed * 1.2)

    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=0.5, colour=list(colour))
        .velocity_directional(
            min_speed=min_speed,
            max_speed=max_speed,
            direction=dir,
            angle_spread=[10, 10],
            angle_dist=None
        )
        .fade(speed=5)
        .lifetime(frames=50)
        .build()
    )


def liquid_splash(pos, game_objects, *, colour, vel_scale=1.0, dir_angle=-90):#twoD liquid
    """
    colour: [r,g,b,a]
    vel_scale: scales the initial speed range
    dir_angle: direction angle in degrees for initial ejection.
              Default -90 = up (pygame coords). Use +90 for down.
    """

    min_speed = 7 * vel_scale
    max_speed = 14 * vel_scale

    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=1, gradient=0, colour=list(colour))
        .velocity_directional(
            min_speed=min_speed,
            max_speed=max_speed,
            direction=int(dir_angle),
            angle_spread=[25, 25],
            angle_dist="normal"
        )
        .gravity(scale=1)     # gravity pull; tweak if your world gravity differs
        .fade(speed=0.3)
        .lifetime(frames=100)
        .build()
    )

def drop(pos, game_objects, *, colour, gravity_scale=0.2):#wet status
    return (
        ParticleBuilder(pos, game_objects)
        .circle(scale=1, gradient=0, colour=list(colour))
        # gentle upward start (dir up, small speed)
        .velocity_directional(
            min_speed=0,
            max_speed=1,
            direction=-90,         
            angle_spread=[10, 10],
            angle_dist="normal"
        )
        .gravity(scale=gravity_scale)  # slight pull down over time
        .fade(speed=2)
        .lifetime(frames=50)
        .build()
    )

def floaty_ambient(pos, game_objects, *, colour=(255,255,255,255)):#flower butter fly
    # random initial direction
    angle = random.randint(0, 360)

    return (
        ParticleBuilder(pos, game_objects)
        .floaty_particles(colour=list(colour))
        .velocity_directional(
            min_speed=0.1,
            max_speed=1.0,
            direction=angle,
            angle_spread=[0, 0],
            angle_dist=None
        )
        .wave(gravity_scale=0.2, frequency=0.15, amplitude=0.6)  # floaty wobble
        .fade(speed=0.5)
        .lifetime(frames=180)
        .build()
    )
PRESETS = {
    "spirit_aura": spirit_aura,
    "converging_soul": converging_soul,
    'burst': burst,
    "spirit_wisp": spirit_wisp,
    "sword_hit": sword_hit,
    "sword_clash": sword_clash,  
    'spark_scatter': spark_scatter,  
    'circle_wave':circle_wave,
    'tiny_trail': tiny_trail,
    'liquid_splash': liquid_splash,
    'drop': drop,
    'floaty_ambient':floaty_ambient,
}



# Option 2: Direct (maximum control)
#particle = Circle(pos, game_objects, radius=5)
#particle.velocity = [7, -8]
#particle.lifetime = 120
#particle.add_component(GravityMotion(particle))
#particle.add_component(FadeComponent(particle))
#particle.add_component(LifetimeComponent(particle))