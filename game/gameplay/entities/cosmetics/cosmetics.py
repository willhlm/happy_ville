import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.base.static_entity import StaticEntity

#cosmetics
class Blood(AnimatedEntity):
    def __init__(self, pos, game_objects, dir = [1,0]):
        super().__init__(pos, game_objects)
        self.sprites = Blood.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Blood.sprites = read_files.load_sprites_dict('assets/sprites/GFX/blood/death/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Dusts(AnimatedEntity):#dust particles when doing things
    def __init__(self, pos, game_objects, dir = [1,0], state = 'one'):
        super().__init__(pos, game_objects)
        self.sprites = Dusts.sprites
        self.image = self.sprites[state][0]
        self.animation.play(state)
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Dusts.sprites = read_files.load_sprites_dict('assets/sprites/GFX/dusts/', game_objects, flip_x = True)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Water_running_particles(AnimatedEntity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Water_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Water_running_particles.sprites = read_files.load_sprites_dict('assets/sprites/animations/running_particles/water/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Grass_running_particles(AnimatedEntity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Grass_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Grass_running_particles.sprites = read_files.load_sprites_dict('assets/sprites/animations/running_particles/grass/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Dust_running_particles(AnimatedEntity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Dust_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Dust_running_particles.sprites = read_files.load_sprites_dict('assets/sprites/animations/running_particles/dust/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Player_Soul(AnimatedEntity):#the thing that popps out when player dies
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Player_Soul.sprites
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name='once')

        self.timer = 0
        self.velocity = [0,0]

    def pool(game_objects):
        Player_Soul.sprites = read_files.load_sprites_dict('assets/sprites/enteties/soul/', game_objects)

    def update(self, dt):
        super().update(dt)
        self.update_pos()
        self.timer += dt
        if self.timer > 100:#fly to sky
            self.velocity[1] = -20
        elif self.timer>200:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0], self.true_pos[1] + self.velocity[1]]
        self.rect.topleft = self.true_pos

    def release_texture(self):
        pass

class ThunderBall(AnimatedEntity):#for thunder dive
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ThunderBall.sprites
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name='once')

    def pool(game_objects):
        ThunderBall.sprites = read_files.load_sprites_dict('assets/sprites/enteties/soul/', game_objects)

    def release_texture(self):
        pass

class ThunderSpark(AnimatedEntity):#when landing thunder dive
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ThunderSpark.sprites
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.currentstate = states_basic.Death(self)

    def pool(game_objects):
        ThunderSpark.sprites = read_files.load_sprites_dict('assets/sprites/animations/thunder_spark/', game_objects)

    def release_texture(self):
        pass

class Spawneffect(AnimatedEntity):#the thing that crets when aila re-spawns
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/GFX/spawneffect/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.finish = False#needed for the cutscene

    def reset_timer(self):
        self.finish = True
        self.kill()

class Slash(AnimatedEntity):#thing that pop ups when take dmg or give dmg: GFX
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Slash.sprites
        state = str(random.randint(1, 3))
        self.animation.play('slash_' + state)
        self.image = self.sprites['slash_' + state][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos

    def pool(game_objects):#all things that should be saved in object pool
        Slash.sprites = read_files.load_sprites_dict('assets/sprites/GFX/slash/',game_objects)

    def reset_timer(self):
        self.kill()

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Rune_symbol(AnimatedEntity):#the stuff that will be blitted on uberrunestone
    def __init__(self,pos,game_objects,ID_key):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/rune_symbol/' + ID_key + '/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        pass

class Thunder_aura(AnimatedEntity):#the auro around aila when doing the thunder attack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/thunder_aura/',game_objects)
        self.currentstate = states_basic.Once(self,next_state = 'Idle',animation_name='idle')#
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()#pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)

    def update(self, dt):
        super().update(dt)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):#called when animation is finished
        super().reset_timer()
        self.currentstate.handle_input('Idle')

class Pray_effect(AnimatedEntity):#the thing when aila pray
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Pray_effect.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def pool(game_objects):
        Pray_effect.sprites = read_files.load_sprites_dict('assets/sprites/animations/pray_effect/', game_objects)

    def spawn(self):
        pass

    def reset_timer(self):
        self.kill()

    def release_texture(self):
        pass

class Health_bar(AnimatedEntity):
    def __init__(self,entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/health_bar/',entity.game_objects)
        self.entity = entity#the boss
        self.max_health = entity.health
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.width = self.rect[2]
        self.rect.topleft = [self.game_objects.game.window_size[0]*0.5 - self.width*0.5,3]

    def resize(self):#in principle, should just be called when boss take dmg
        width = max(self.width * (self.entity.health/self.max_health),0)
        for index, sprite in  enumerate(self.sprites['idle']):
            self.sprites['idle'][index] = pygame.transform.scale(sprite,[width,self.rect[3]])

class Logo_loading(AnimatedEntity):
    def __init__(self, game_objects):
        super().__init__([500,300], game_objects)
        self.sprites = Logo_loading.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.animation.framerate = 0.1#makes it slower

    def pool(game_objects):
        Logo_loading.sprites = read_files.load_sprites_dict('assets/sprites/UI/logo_loading/',game_objects)

    def update(self, dt):
        super().update(dt)
        self.rect.topleft = [self.true_pos[0] + self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1] + self.game_objects.camera_manager.camera.scroll[1]]

    def release_texture(self):
        pass

    def reset_timer(self):
        self.kill()

class Twinkle(AnimatedEntity):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Twinkle.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

    def reset_timer(self):
        super().reset_timer()
        self.kill()

    def release_texture(self):
        pass

    def pool(game_objects):
        Twinkle.sprites = read_files.load_sprites_dict('assets/sprites/GFX/twinkle/', game_objects)

class InteractableIndicator(StaticEntity):#the hoovering above things to indicat it is interactable, or only for NPC?
    def __init__(self, pos, game_objects, size = (32,32)):
        super().__init__(pos, game_objects)
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        InteractableIndicator.image = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self, dt):
        self.time += dt * 0.1
        self.update_vel()
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0] * dt, self.true_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)

class ConversationBubbles(StaticEntity):#the thing npcs have hoovering above them for random messages
    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)
        self.render_text(text)

        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        ConversationBubbles.layer = game_objects.game.display.make_layer(size)
        ConversationBubbles.bg = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self, dt):
        self.time += dt * 0.1
        self.update_vel()
        self.update_pos(dt)
        self.lifetime -= dt
        if self.lifetime < 0:
            self.kill()

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*dt,self.true_pos[1] + self.velocity[1]*dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)

    def render_text(self, text):
        texture = self.game_objects.font.render(text = text)
        self.game_objects.game.display.render(self.bg, self.layer)#shader render
        self.game_objects.game.display.render(texture, self.layer, position = [10, self.rect[3]])#shader render
        self.image = self.layer.texture
        texture.release()

#shader base     
class Thunder_ball(StaticEntity):#not used
    def __init__(self, pos, game_objects, size, praalalx):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.time = 0

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['thunder_ball']['iTime'] = self.time
        self.game_objects.shaders['thunder_ball']['iResolution'] = self.size

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['thunder_ball'])#shader render        

class Smoke(StaticEntity):#2D smoke
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.hitbox = pygame.Rect(pos, size)
        self.time = 0
        self.size = size

        self.colour = properties.get('colour', (1,1,1,1))
        self.spawn_rate = int(properties.get('spawn_rate', 10))
        self.radius = properties.get('radius', 0.03)
        self.speed = properties.get('speed', 0.2)
        self.horizontalSpread = properties.get('horizontalSpread', 0.5)
        self.lifetime = properties.get('lifetime', 2)
        self.spawn_position = properties.get('spawn_position', (0.5, 0.0))

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['smoke']['noiseTexture'] = self.noise_layer.texture
        self.game_objects.shaders['smoke']['time'] = self.time*0.01
        self.game_objects.shaders['smoke']['textureSize'] = self.size

        self.game_objects.shaders['smoke']['baseParticleColor'] = self.colour
        self.game_objects.shaders['smoke']['spawnRate'] = self.spawn_rate
        self.game_objects.shaders['smoke']['baseParticleRadius'] = self.radius
        self.game_objects.shaders['smoke']['baseParticleSpeed'] = self.speed
        self.game_objects.shaders['smoke']['horizontalSpread'] = self.horizontalSpread
        self.game_objects.shaders['smoke']['particleLifetime'] = self.lifetime
        self.game_objects.shaders['smoke']['spawnPosition'] = self.spawn_position

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture,target, position = pos, shader = self.game_objects.shaders['smoke'])#shader render        

class Death_fog(StaticEntity):#2D explosion
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.size = size
        self.time = 0

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['death_fog']['TIME'] = self.time*0.01
        self.game_objects.shaders['death_fog']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['death_fog']['velocity'] = [0, 0]
        self.game_objects.shaders['death_fog']['fog_color'] = [0, 0, 0, 1]

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['death_fog'])#shader render
      