from engine import constants as C

from .base import BaseState


class Idle(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['idle']

    def handle_input(self, input_name, **kwarg):
        if input_name == 'hurt':
            self.enter_state('Hurt', **kwarg)
        elif input_name == 'outline':
            self.enter_state('Outline', **kwarg)
        elif input_name == 'alpha':
            self.enter_state('Alpha')


class Hurt(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.duration = C.hurt_animation_length
        self.shader = self.entity.game_objects.shaders['shock_damage']
        self.next_animation = 'Idle'
        self.time = 0
        self.amplitude = kwarg.get('amplitude', 1) * 0.08
        self.frequency = kwarg.get('frequency', 50)
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.decay_rate = kwarg.get('decay_rate', 5)
        self.direction = kwarg.get('direction', [1, 0])
        self.alpha_decay = kwarg.get('alpha_decay', 0.974)

    def set_uniforms(self):
        self.shader['time'] = self.time * 0.01
        self.shader['frequency'] = self.frequency
        self.shader['amplitude'] = self.amplitude
        self.colour[-1] *= self.alpha_decay
        self.shader['colour'] = self.colour
        self.shader['decay_rate'] = self.decay_rate
        self.shader['direction'] = self.direction

    def update_render(self, dt):
        self.duration -= dt
        self.time += dt
        if self.duration < 0:
            self.enter_state(self.next_animation)

    def handle_input(self, input_name, **kwarg):
        if input_name == 'invincibile':
            self.next_animation = 'Invincibile'


class Invincibile(BaseState):
    def __init__(self, entity):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['invincible']
        self.duration = C.invincibility_time_player - (C.hurt_animation_length + 1)
        self.time = 0

    def update_render(self, dt):
        self.duration -= dt
        self.time += 0.5 * dt
        if self.duration < 0:
            self.enter_state('Idle')

    def set_uniforms(self):
        self.shader['time'] = self.time


class Alpha(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.alpha = self.entity.game_objects.fade.create(
            "alpha",
            kwarg.get('alpha', 255),
            on_complete=kwarg.get('on_complete', self.entity.kill),
        )
        self.fade_rate = kwarg.get('fade_rate', 0.9)
        self.kill_threshold = kwarg.get('kill_threshold', 5)

    def update_render(self, dt):
        self.alpha.decay(self.fade_rate)
        if self.alpha.is_below(self.kill_threshold):
            self.alpha.complete()

    def draw(self, base_texture, target, position, flip, angle):
        self.alpha.render(
            base_texture,
            target,
            position=position,
            flip=flip,
            angle=angle,
        )
        return target


class Teleport(BaseState):
    def __init__(self, entity):
        super().__init__(entity)
        self.time = 0
        self.shader = entity.game_objects.shaders['teleport']

    def update_render(self, dt):
        self.time += 0.01
        if self.time >= 1:
            self.entity.kill()

    def set_uniforms(self):
        self.shader['progress'] = self.time


class Dissolve(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.noise_layer = self.entity.game_objects.game.display.make_layer(self.entity.image.size)
        self.empty = self.entity.game_objects.game.display.make_layer(self.entity.image.size)
        self.shader = self.entity.game_objects.shaders['dissolve']
        self.time = 0
        self.colour = kwarg.get('colour', [1, 0, 0, 1])
        self.size = kwarg.get('size', 0.1)
        self.duration = kwarg.get('duration', 100)
        self.on_complete = kwarg.get('on_complete', self.entity.kill)

    def update_render(self, dt):
        self.time += dt * 0.1
        if self.time >= 1 or self.duration <= 0:
            self.finish()
            return
        self.duration -= dt

    def set_uniforms(self):
        self.empty.clear(0, 0, 0, 0)
        self.entity.game_objects.shaders['noise_perlin']['u_resolution'] = self.entity.image.size
        self.entity.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.entity.game_objects.shaders['noise_perlin']['scroll'] = [0, 0]
        self.entity.game_objects.shaders['noise_perlin']['scale'] = [10, 10]
        self.entity.game_objects.game.display.render(
            self.empty.texture,
            self.noise_layer,
            shader=self.entity.game_objects.shaders['noise_perlin'],
        )
        self.entity.game_objects.shaders['dissolve']['dissolve_texture'] = self.noise_layer.texture
        self.entity.game_objects.shaders['dissolve']['dissolve_value'] = max(1 - self.time, 0)
        self.entity.game_objects.shaders['dissolve']['burn_color'] = self.colour
        self.entity.game_objects.shaders['dissolve']['burn_size'] = self.size


class Swirl(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['swirl']
        self.ratio = 1

    def update_render(self, dt):
        self.ratio -= dt * 0.01
        self.ratio = max(0, self.ratio)
        if self.ratio <= 0:
            self.enter_state('Idle')

    def set_uniforms(self):
        self.shader['ratio'] = self.ratio

