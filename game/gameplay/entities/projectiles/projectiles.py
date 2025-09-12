import pygame, math
from gameplay.entities.projectiles.base.projectiles import Projectiles
from gameplay.entities.projectiles.base.melee import Melee
from engine.utils import read_files
from gameplay.entities.projectiles import seeds
from gameplay.visuals.particles import particles

#projectiles
class Bouncy_balls(Projectiles):#for ball challange room
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Bouncy_balls.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.light = game_objects.lights.add_light(self)
        self.velocity = [random.uniform(-10,10),random.uniform(-10,-4)]

    def pool(game_objects):
        Bouncy_balls.sprites = read_files.load_sprites_dict('assets/sprites/attack/projectile_1/',game_objects)

    def release_texture(self):
        pass

    def kill(self):#when lifeitme runs out or hit by aila sword
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def take_dmg(self, dmg):#when hit by aila sword without purple stone
        self.velocity = [0,0]
        self.dmg = 0
        self.currentstate.handle_input('Death')
        self.game_objects.signals.emit('ball_killed')

    #platform collisions
    def right_collision(self, block, type = 'Wall'):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self, block, type = 'Wall'):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self, block):
        self.hitbox.bottom = block.hitbox.top
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

class Poisoncloud(Projectiles):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Poisoncloud.sprites
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.lifetime=400

    def pool(game_objects):
        Poisoncloud.sprites = read_files.load_sprites_dict('assets/sprites/attack/poisoncloud/',game_objects)

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.currentstate.handle_input('Death')

class Poisonblobb(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Poisonblobb.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 100)
        self.dir = kwarg.get('dir', [1, -1])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [-amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)

    def update_vel(self, dt):
        self.velocity[1] += 0.1 * dt#graivity

    def take_dmg(self, dmg):#aila sword without purple stone
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def collision_platform(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def pool(game_objects):
        Poisonblobb.sprites = read_files.load_sprites_dict('assets/sprites/attack/poisonblobb/', game_objects)

class Projectile_1(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Projectile_1.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 200)
        self.dir = kwarg.get('dir', [1, 0])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def pool(game_objects):
        Projectile_1.sprites = read_files.load_sprites_dict('assets/sprites/attack/projectile_1/',game_objects)

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)

    def update_vel(self, dt):
        self.velocity[1] += 0.05 * dt#gravity

    def collision_platform(self,platform):
        self.flags['aggro'] = False
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def take_dmg(self, dmg):#called when fprojicle collides
        self.collision_platform(None)

class Falling_rock(Projectiles):#things that can be placed in cave, the source makes this and can hurt player
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Falling_rock.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.dmg = 1
        self.currentstate = states_droplets.Idle(self)

    def pool(game_objects):
        Falling_rock.sprites = read_files.load_sprites_dict('assets/sprites/animations/falling_rock/rock/', game_objects)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        super().collision_enemy(collision_enemy)
        self.currentstate.handle_input('death')

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        super().collision_platform(collision_plat)
        self.currentstate.handle_input('death')

class Droplet(Projectiles):#droplet that can be placed, the source makes this and can hurt player
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Droplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.currentstate = states_droplets.Idle(self)

        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            self.dmg = 1#acid
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more
        else:
            self.dmg = 0#water
            self.shader_state = states_shader.Idle(self)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_enemy(collision_enemy)

    def collision_platform(self, collision_plat):#collision platform
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_platform(collision_plat)

    def pool(game_objects):
        Droplet.sprites = read_files.load_sprites_dict('assets/sprites/animations/droplet/droplet/', game_objects)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)

class SlamAttack(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = SlamAttack.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate.enter_state('Death')
        self.animation.play('idle')
        self.dir = kwarg.get('dir', [1, 0])
        self.dmg = 1

    def pool(game_objects):
        SlamAttack.sprites = read_files.load_sprites_dict('assets/sprites/attack/slam/', game_objects, flip_x = True)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        collision_enemy.take_dmg(dmg = self.dmg, effects = [lambda: collision_enemy.knock_back(amp = [50, 0], dir = self.dir)])

    def collision_platform(self, collision_plat):#collision platform
        pass

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)

class Hurt_box(Melee):#a hitbox that spawns
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = pygame.Rect(entity.rect.topleft, kwarg.get('size', [64, 64]))
        self.dmg = kwarg.get('dmg', 1)

    def update_render(self, dt):
        pass

    def update(self, dt):
        self.lifetime -= dt
        self.destroy()

    def draw(self, target):
        pass

class Explosion(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = Explosion.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.dir = [0, 0]
        self.lifetime = 100
        self.dmg = 1

    def pool(game_objects):
        Explosion.sprites = read_files.load_sprites_dict('assets/sprites/attack/explosion/', game_objects)

    def reset_timer(self):
        self.kill()

class Counter(Melee):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = self.entity.hitbox.copy()
        self.dmg = 0
        self.entity.flags['invincibility'] = True#make the player invincible

    def update(self, dt):
        self.lifetime -= dt
        self.destroy()

    def collision_enemy(self, collision_enemy):
        self.counter()

    def collision_projectile(self, eprojectile):
        self.counter()

    def counter(self):
        if self.flags['invincibility']: return#such that it only collides ones
        self.flags['invincibility'] = True
        self.entity.game_objects.timer_manager.start_timer(C.invincibility_time_player, self.entity.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.entity.abilities.spirit_abilities['Slow_motion'].counter()#slow motion

    def kill(self):
        super().kill()
        self.entity.abilities.spirit_abilities['Slow_motion'].exit()

    def draw(self, target):
        pass

class Sword(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width*2,self.image.height*2)
        self.hitbox = self.rect.copy()

    def pool(game_objects):
        Sword.sprites = read_files.load_sprites_dict('assets/sprites/attack/sword/', game_objects)

    def init(self):
        self.sprites = Sword.sprites
        self.image = self.sprites['idle'][0]
        self.dmg = self.entity.dmg
        self.lifetime = 10

    def collision_enemy(self, collision_enemy):
        if collision_enemy.flags['invincibility']: return
        collision_enemy.take_dmg(dmg = self.dmg, effects = [lambda: collision_enemy.knock_back(amp = [50, 0], dir = self.dir), lambda: collision_enemy.emit_particles(dir = self.dir)])#TODO insead of lambdas, we could/should maybe change to class based effects
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        self.clash_particles(collision_enemy.hitbox.center, lifetime = 20, dir = random.randint(-180, 180))

    def clash_particles(self, pos, number_particles = 12, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, **kwarg)
            self.entity.game_objects.cosmetics.add(obj1)

class Aila_sword(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/attack/aila_slash/',self.entity.game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/projectiles/aila_sword/')
        self.image = self.sprites['slash_1'][0]
        self.animation.play('slash_1')
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_sword.Slash_1(self)

        self.dmg = 1

        self.tungsten_cost = 1#the cost to level up to next level
        self.stones = {}#{'red': Red_infinity_stone([0,0], entity.game_objects, entity = self), 'green': Green_infinity_stone([0,0], entity.game_objects, entity = self), 'blue': Blue_infinity_stone([0,0],entity.game_objects, entity = self),'orange': Orange_infinity_stone([0,0],entity.game_objects, entity = self),'purple': Purple_infinity_stone([0,0], entity.game_objects, entity = self)}#gets filled in when pick up stone. used also for inventory
        self.swing = 0#a flag to check which swing we are at (0 or 1)
        self.stone_states = {'enemy_collision': states_sword.Stone_states(self), 'projectile_collision': states_sword.Stone_states(self), 'slash': states_sword.Stone_states(self)}#infinity stones can change these to do specific things
        
    def use_sword(self, swing = 'light'):#called from player stetas whenswing sword
        self.stone_states['slash'].slash_speed()
        particle = {'dir': self.dir,'lifetime': 180,'scale': 5,'angle_spread': [13, 15],'angle_dist': 'normal','colour': C.spirit_colour,'gravity_scale': -0.1,'gradient': 1,'fade_scale': 2.2,'number_particles': 8,'vel': {'ejac': [13, 17]}}
        self.effects = hit_effects.HitEffect(sound = self.sounds['sword_hit_enemy'][0], particles = particle, knockback = (25, 10), hitstop = 10)

    def update_hitbox(self):
        hitbox_attr, entity_attr = self.direction_mapping[tuple(self.dir)]#self.dir is set in states_sword
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate.update_rect()

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with projectile
        if eprojectile.flags['invincibility']: return
        eprojectile.flags['invincibility'] = True
        self.entity.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, eprojectile.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.stone_states['projectile_collision'].projectile_collision(eprojectile)

    def collision_enemy(self, collision_enemy):
        self.currentstate.sword_jump()
        if collision_enemy.take_dmg(dmg = self.dmg):
            modified_effect = collision_enemy.modify_hit(self.effects)
            modified_effect.apply(self, collision_enemy)
            collision_enemy.currentstate.handle_input('sword')
            self.stone_states['enemy_collision'].enemy_collision()

    def clash_particles(self, pos, number_particles=12):
        angle = random.randint(-180, 180)#the erection anglex
        color = [255, 255, 255, 255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, distance = 0, lifetime = 10, vel = {'linear':[5,7]}, dir = angle, scale = 0.8, fade_scale = 7, colour = color)
            self.entity.game_objects.cosmetics.add(obj1)

    def level_up(self):#called when the smith imporoves the sword
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.tungsten_cost += 2#1, 3, 5 tungstes to level up

    def draw(self, target):
        pass

class Arrow(Projectiles):#should it be called seed?
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Arrow.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100

        self.dir = kwarg.get('dir', [1, 0])
        normalise = (self.dir[0] ** 2 + self.dir[1] ** 2)**0.5
        amp = kwarg.get('time', 0)/50#50 is the charge duration, how long one sohuld press to reach max speed
        amp = min(amp, 1)#limit the max charge to 1

        self.velocity = [amp * self.dir[0] * 20 / normalise, amp * self.dir[1] * 20 / normalise]
        self.seed_spawner = seeds.SeedSpawner(self)

        self.once = False

        self.acceleration = [0, 0.1]
        self.friction = [0.01, 0.01]
        self.max_vel = [10, 10]

    def update_vel(self, dt):#called from hitsop_states
        self.velocity[1] += dt * (self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)
        self.angle = self._get_trajectory_angle()
        self.emit_particles(lifetime = 50, dir = self.dir, vel = {'linear': [self.velocity[0] * 0.1, self.velocity[1] * 0.1]}, scale = 0.5, fade_scale = 5)

    def emit_particles(self, type = 'Circle', **kwarg):
        obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
        self.game_objects.cosmetics.add(obj1)

    def _get_trajectory_angle(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0)#shader render

    def pool(game_objects):
        Arrow.sprites = read_files.load_sprites_dict('assets/sprites/attack/arrow/', game_objects)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        self.kill()

    def collision_interactables(self,interactable):#collusion interactables
        pass

    def collision_interactables_fg(self, interactable):#collusion interactables_fg: e.g. twoDliquid
        if self.once: return
        self.once = True
        interactable.seed_collision(self)
        self.velocity = [0,0]
        self.kill()

    def collision_enemy(self,collision_enemy):
        self.kill()

    def right_collision(self, block, type = 'Wall'):
        self.collision_platform([1, 0], block)

    def left_collision(self, block, type = 'Wall'):
        self.collision_platform([-1, 0], block)

    def down_collision(self, block):
        self.collision_platform([0, -1], block)

    def top_collision(self, block):
        self.collision_platform([0, 1], block)

    def collision_platform(self, dir, block):
        self.velocity = [0,0]
        if self.once: return
        self.once = True
        self.seed_spawner.spawn_seed(block, dir)
        self.kill()

class Wind(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Wind.image
        self.rect = pygame.Rect(pos[0], pos[1], self.image.texture.width, self.image.texture.height)
        self.hitbox = self.rect.copy()
        self.dmg = 0

        self.time = 0

        self.dir = kwarg.get('dir', [1,0])
        self.velocity = [self.dir[0] * 10, self.dir[1] * 10]

    def collision_platform(self, platform):
        self.velocity = [0,0]
        self.kill()

    def pool(game_objects):
        size = [32, 32]
        Wind.image = game_objects.game.display.make_layer(size)

    def collision_enemy(self, collision_enemy):#if hit something
        self.velocity = [0,0]
        collision_enemy.velocity[0] = self.dir[0]*40#abs(push_strength[0])
        collision_enemy.velocity[1] = -1
        self.kill()

    def update(self, dt):
        self.time += dt
        self.lifetime -= dt
        self.destroy()

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture,target, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render

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