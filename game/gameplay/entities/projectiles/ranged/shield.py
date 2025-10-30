import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles

class Shield(Projectiles):#a protection shield
    def __init__(self, entity, **kwarg):
        super().__init__(entity.hitbox.topleft, entity.game_objects)
        self.entity = entity

        self.size = Shield.size
        self.empty = Shield.empty
        self.noise_layer = Shield.noise_layer
        self.screen_layer = Shield.screen_layer
        self.image = Shield.image

        self.rect = pygame.Rect(entity.hitbox.center, self.size)
        self.hitbox = self.rect.copy()
        self.reflect_rect = self.hitbox.copy()

        self.time = 0
        self.health = kwarg.get('health', 1)
        self.lifetime = kwarg.get('lifetime', 100)
        self.die = False
        self.progress = 0

    def take_dmg(self, dmg):#called when entity takes damage
        if self.flags['invincibility']: return
        self.health -= dmg

        self.flags['invincibility'] = True
        if self.health > 0:#TODO make it red momentary or something to indicate that it too damage
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        else:
            self.game_objects.timer_manager.start_timer(100, self.time_out)#adds a timer to timer_manager and sets self.invincible to false after a while
            #TODO make it blink or something to indicate that it will die soon

    def time_out(self):#called when general timer it count down
        self.kill()

    def update(self, dt):
        self.time += dt
        if self.time > self.lifetime:
            self.die = True
            self.progress += dt*0.005
            if self.progress >= 1:
                self.kill()
        self.update_pos()

    def update_pos(self):
        self.true_pos = [int(self.entity.hitbox.center[0] - self.game_objects.camera_manager.camera.scroll[0] - 90*0.5),int(self.entity.hitbox.center[1] - self.game_objects.camera_manager.camera.scroll[1]- 90*0.5)]
        self.rect.topleft = self.hitbox.center

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game_objects.shaders['noise_perlin']['scroll'] = [0, 0]
        self.game_objects.shaders['noise_perlin']['scale'] = [3,3]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #cut out the screen
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = 'player', include = True)#make a copy of the screen
        self.reflect_rect.bottomleft = [self.hitbox.topleft[0], 640 - self.hitbox.topleft[1] + 90 - 10]
        self.game_objects.game.display.render(screen_copy.texture, self.screen_layer, section = self.reflect_rect)

        self.game_objects.shaders['shield']['TIME'] = self.time*0.001
        self.game_objects.shaders['shield']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['shield']['screen_tex'] = self.screen_layer.texture

        if not self.die:#TODO
            self.game_objects.game.display.render(self.empty.texture, self.image, shader = self.game_objects.shaders['shield'])#shader render
            self.game_objects.game.display.render(self.image.texture, target, position = self.hitbox.topleft)#shader render
        else:
            self.game_objects.shaders['dissolve']['dissolve_texture'] = self.noise_layer.texture
            self.game_objects.shaders['dissolve']['dissolve_value'] = max(1 - self.progress,0)
            self.game_objects.shaders['dissolve']['burn_size'] = 0.0
            self.game_objects.shaders['dissolve']['burn_color'] = [0.39, 0.78, 1,0.7]

            self.game_objects.game.display.render(self.empty.texture, self.image, shader = self.game_objects.shaders['shield'])#shader render
            self.game_objects.game.display.render(self.image.texture, target, position = self.hitbox.topleft, shader = self.game_objects.shaders['dissolve'])#shader render

    def pool(game_objects):
        Shield.size = [90, 90]
        Shield.empty = game_objects.game.display.make_layer(Shield.size)
        Shield.noise_layer = game_objects.game.display.make_layer(Shield.size)
        Shield.screen_layer = game_objects.game.display.make_layer(Shield.size)
        Shield.image = game_objects.game.display.make_layer(Shield.size)

    def kill(self):
        super().kill()
        self.entity.abilities.spirit_abilities['Shield'].shield_expire()

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        pass

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        pass
