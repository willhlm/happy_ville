import pygame
from engine import constants as C
from gameplay.entities.visuals.particles import particles
from gameplay.entities.base.static_entity import StaticEntity
from . import states_two_d_liquid

class TwoDLiquid(StaticEntity):#inside interactables_fg group. fg because in front of player
    def __init__(self, pos, game_objects, size, layer_name, **properties):
        super().__init__(pos, game_objects)
        self.empty = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        if layer_name == 'bg1':
            layer_name = 'player'
        
        self.layer_name = layer_name

        self.hitbox = pygame.Rect(pos, size)#for player collision
        self.interacted = False#for player collision

        self.time = 0
        self.size = size

        self.shader = game_objects.shaders['twoD_liquid']
        self.shader['u_resolution'] = self.game_objects.game.window_size
        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            if not properties.get('vertical', False):
                self.hole = Hole(pos, game_objects, size)#for poison
                self.currentstate = states_two_d_liquid.Poison(self, **properties)
            else:#vertical scroller -> golden fields
                self.currentstate = states_two_d_liquid.Poison_vertical(self, **properties)
        else:
            self.currentstate = states_two_d_liquid.Water(self, **properties)

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt
        self.currentstate.update()

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
        self.game_objects.shaders['twoD_liquid']['SCREEN_TEXTURE'] = screen_copy.texture#for some reason, the water fall there, making it flicker. offsetting the cutout part, the flickering appears when the waterfall enetrs
        self.game_objects.shaders['twoD_liquid']['TIME'] = self.time * 0.01

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.shaders['twoD_liquid']['section'] = [pos[0], pos[1], self.size[0], self.size[1]]

        self.game_objects.game.display.render(self.empty.texture, target, position = pos, shader = self.shader)#shader render

    def collision(self, player):#player collision
        if self.interacted: return
        player.movement_manager.add_modifier('two_d_liquid')
        vel_scale = player.velocity[1] / C.max_vel[1]
        self.splash(player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [7 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        player.timer_jobs['wet'].deactivate()#stop dropping if inside the water again
        self.interacted = True
        self.currentstate.player_collision(player)

    def noncollision(self, player):
        if not self.interacted: return
        self.game_objects.player.movement_manager.remove_modifier('two_d_liquid')
        self.game_objects.player.timer_jobs['wet'].activate(self.currentstate.liquid_tint)#water when player leaves
        vel_scale = abs(self.game_objects.player.velocity[1] / C.max_vel[1])
        self.splash(self.game_objects.player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [10 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        self.interacted = False
        self.currentstate.player_noncollision()

    def splash(self,  pos, number_particles=20, **kwarg):#called from states, upoin collusions
        for i in range(0, number_particles):
            obj1 = particles.Circle(pos, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

    def seed_collision(self, seed):
        vel_scale = [abs(seed.velocity[0])/20,abs(seed.velocity[1])/ 20]
        self.splash(seed.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [14 * vel_scale[0], 7 * vel_scale[0]]}, fade_scale = 0.3, gradient=0, scale = 2)
        seed.seed_spawner.spawn_bubble()        