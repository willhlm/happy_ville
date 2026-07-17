import pygame
from engine import constants as C
from gameplay.entities.base.static_entity import StaticEntity
from . import liquid_behaviors

class TwoDLiquid(StaticEntity):
    def __init__(self, pos, game_objects, size, layer_name, **properties):
        super().__init__(pos, game_objects)
        self.empty = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        if layer_name == 'bg1':
            layer_name = 'player'
        
        self.layer_name = layer_name

        self.full_hitbox = pygame.Rect(pos, size)
        self.hitbox = self.full_hitbox.copy()#for player collision

        self.time = 0
        self.size = size
        self.base_transparent_top_pixels = float(properties.get("transparent_top_pixels", 5.0))
        self.darker_region_height_pixels = float(properties.get("darker_region_height_pixels", 6.0))
        self.height_percent = properties.get("height", 100.0)
        self.transparent_top_pixels = self.base_transparent_top_pixels

        self.shader = game_objects.shaders['twoD_liquid']
        self.shader['u_resolution'] = self.game_objects.game.window_size
        self.shader['darkerRegionHeightPixels'] = self.darker_region_height_pixels
        self.set_height_percent(self.height_percent)
        if game_objects.world_state.narrative.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            if not properties.get('vertical', False):
                self.behavior = liquid_behaviors.PoisonBehavior(self, **properties)
            else:#vertical scroller -> golden fields
                self.behavior = liquid_behaviors.VerticalPoisonBehavior(self, **properties)
        else:
            self.behavior = liquid_behaviors.WaterBehavior(self, **properties)

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt
        self.behavior.update()

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = self.layer_name, include = True)

        #water
        self.game_objects.shaders['twoD_liquid']['refraction_map'] = self.noise_layer.texture
        self.game_objects.shaders['twoD_liquid']['SCREEN_TEXTURE'] = screen_copy.texture
        self.game_objects.shaders['twoD_liquid']['TIME'] = self.time * 0.01

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.shaders['twoD_liquid']['section'] = [pos[0], pos[1], self.size[0], self.size[1]]

        self.game_objects.game.display.render(self.empty.texture, target, position = pos, shader = self.shader)#shader render

    def collision(self, entity):
        pass

    def on_collision(self, entity):#player collision
        entity.movement_modifier.add_modifier('two_d_liquid')
        vel_scale = max(entity.velocity[1] / C.max_vel[1], 0.5)
        self.splash(entity.hitbox.midbottom, vel_scale)
        #self.splash(entity.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.behavior.liquid_tint[0]*255, self.behavior.liquid_tint[1]*255, self.behavior.liquid_tint[2]*255, 255], vel = {'gravity': [7 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        if hasattr(entity, 'status_component'):
            entity.status_component.deactivate('wet')#stop dropping if inside the water again
        self.behavior.on_enter(entity)

    def on_noncollision(self, entity):
        entity.movement_modifier.remove_modifier('two_d_liquid')
        if hasattr(entity, 'status_component'):
            entity.status_component.activate('wet', self.behavior.liquid_tint)#water when player leaves
        vel_scale = max(entity.velocity[1] / C.max_vel[1], 0.5)
        self.splash(entity.hitbox.midbottom, vel_scale)
        #self.splash(entity.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.behavior.liquid_tint[0]*255, self.behavior.liquid_tint[1]*255, self.behavior.liquid_tint[2]*255, 255], vel = {'gravity': [10 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        self.behavior.on_exit(entity)

    def splash(self,  pos, vel_scale, number_particles=20):#called from states, upoin collusions
        self.game_objects.particles.emit('liquid_splash', pos, number_particles, colour = [self.behavior.liquid_tint[0]*255, self.behavior.liquid_tint[1]*255, self.behavior.liquid_tint[2]*255, 255],vel_scale = vel_scale)

    def seed_collision(self, seed):
        vel_scale = [abs(seed.velocity[0])/20,abs(seed.velocity[1])/ 20]
        self.splash(seed.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.behavior.liquid_tint[0]*255, self.behavior.liquid_tint[1]*255, self.behavior.liquid_tint[2]*255, 255], vel = {'gravity': [14 * vel_scale[0], 7 * vel_scale[0]]}, fade_scale = 0.3, gradient=0, scale = 2)
        seed.seed_spawner.spawn_bubble()        

    def take_hit(self, effect):
        return False, effect

    def get_surface_top(self):
        return self.hitbox.top + self.base_transparent_top_pixels

    def get_hidden_top_pixels(self):
        visible_ratio = max(0.0, min(self.height_percent, 100.0)) * 0.01
        return self.size[1] * (1.0 - visible_ratio)

    def set_height_percent(self, height_percent):
        self.height_percent = max(0.0, min(float(height_percent), 100.0))
        hidden_top_pixels = self.get_hidden_top_pixels()

        self.transparent_top_pixels = self.base_transparent_top_pixels + hidden_top_pixels
        self.shader['lineHeightPixels'] = self.transparent_top_pixels

        top = self.full_hitbox.top + int(round(hidden_top_pixels))
        height = max(0, self.full_hitbox.bottom - top)
        self.hitbox = pygame.Rect(self.full_hitbox.left, top, self.full_hitbox.width, height)

    def get_height_percent(self):
        return self.height_percent
