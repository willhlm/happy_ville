import pygame 
from gameplay.entities.interactables.base.interactables import Interactables
from engine.utils import read_files
from gameplay.narrative import dialogue
from engine import constants as C
from gameplay.entities.base.static_entity import StaticEntity

from gameplay.entities.states import states_cocoon_boss, runestone_states, loot_container_states, states_savepoint, states_grind, states_lever, states_shader
#interactables
class Place_holder_interacatble(Interactables):
    def __init__(self,entity, game_objects):
        super().__init__(entity.rect.center, game_objects)
        self.entity = entity
        self.hitbox = entity.hitbox

    def update(self, dt):
        pass

    def draw(self, target):
        pass

    def interact(self):#when player press T
        self.entity.interact()

    def release_texture(self):
        pass

class Bubble_source(Interactables):#the thng that spits out bubbles in cave HAWK TUAH!
    def __init__(self, pos, game_objects, bubble, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/bubble_source/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/bubble_source/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()
        self.spawn_timer = prop.get('spawnrate', 180)
        #self.spawn_timer = 180

        self.bubble = bubble#the bubble is in platform, so the reference is sent in init
        self.prop = prop
        #self.time = random.randint(0, 10)
        self.time = -1 * prop.get('init_delay', random.randint(0, 50))

    def group_distance(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        super().update(dt)
        self.time += dt
        if self.time > self.spawn_timer:
            self.game_objects.sound.play_sfx(self.sounds['spawn'][random.randint(0, 1)], vol = 0.3)
            bubble = self.bubble([self.rect.centerx, self.rect.top], self.game_objects, **self.prop)
            #self.game_objects.dynamic_platforms.add(bubble)
            self.game_objects.platforms.add(bubble)
            #self.time = random.randint(0, 10)
            self.time = 0

class Crystal_source(Interactables):#the thng that spits out crystals in crystal mines
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/crystal_source/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.time = 0
        self.frequency = kwarg.get('frequency', 15)
        self.kwarg = kwarg

    def group_distance(self):
        pass

    def update(self, dt):
        super().update(dt)
        self.time += dt
        if self.time > self.frequency:
            crystal = Projectile_1(self.rect.center, self.game_objects, **self.kwarg)
            self.game_objects.eprojectiles.add(crystal)
            self.time = 0

class Challenges(Interactables):#monuments you interact to get quests or challenges
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)

    def render_potrait(self, target):
        pass

    def interact(self):#when plater press t
        if self.interacted: return
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)

        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

    def reset(self):#called when challange is failed
        self.shader_state.handle_input('idle')
        self.interacted = False

class Challenge_monument(Challenges):#the status spawning a portal, balls etc - challange rooms
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/challenges/challenge_monument/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID = ID
        self.interacted = self.game_objects.world_state.quests.get(ID, False)
        self.dialogue = dialogue.Dialogue_interactable(self, ID)#handles dialoage and what to say

        if self.interacted:
            self.shader_state = states_shader.Tint(self, colour = [0,0,0,100])
        else:
            game_objects.lights.add_light(self)
            self.shader_state = states_shader.Idle(self)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest(self.ID.capitalize(), monument = self)

class Stone_wood(Challenges):#the stone "statue" to initiate the lumberjacl quest
    def __init__(self, pos, game_objects, quest, item):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/challenges/stone_wood/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.item = item
        self.quest = quest

        self.interacted = self.game_objects.world_state.quests.get(quest, False)
        self.dialogue = dialogue.Dialogue_interactable(self, quest)#handles dialoage and what to say
        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self)

    def on_interact(self, item, player):#called when the signal is emitted
        if type(item).__name__.lower() == self.item:
            self.game_objects.quests_events.initiate_quest(self.quest, item = self.item)

    def buisness(self):#enters after conversation
        self.game_objects.signals.subscribe('item_interacted', self.on_interact)
        item = getattr(sys.modules[__name__], self.item.capitalize())(self.rect.center, self.game_objects, state = 'wild')#make a class based on the name of the newstate: need to import sys
        self.game_objects.loot.add(item)

class Air_dash_statue(Interactables):#interact with it to get air dash
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/statues/air_dash_statue/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.interacted = self.game_objects.player.states.get('Air_dash', False)

        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self, colour = [0,0,0,100])
        self.text = 'dash in air'

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press t/y
        if self.interacted: return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.game_objects.player.states['Air_dash'] = True#give ability
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites['air_dash_main'][0], text = self.text, callback = self.on_exit)

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item

class Thunder_dive_statue(Interactables):#interact with it to upgrade horagalles rage
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/statues/thunder_dive_statue/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        ability = self.game_objects.player.abilities.spirit_abilities.get('Thunder', False)
        self.interacted = ability and ability.level == 2#if level 2, inteeracted = True

        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self, colour = [0, 0, 0, 100])
        self.text = 'thunder dive in directions'

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press t/y
        if self.interacted: return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        ability = self.game_objects.player.abilities.spirit_abilities['Thunder'].level_up()
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites['thunder_main'][0], text = self.text, callback = self.on_exit)

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item

class Safe_spawn(Interactables):#area which gives the coordinates which will make aila respawn at after falling into a hole
    def __init__(self, pos, game_objects, size, position):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.position = position

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update_render(self, dt):
        pass

    def update(self, dt):
        self.group_distance()

    def player_collision(self, player):
        player.backpack.map.save_safespawn(self.position)

class Hole(Interactables):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.interacted = False

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()
        #print(self.interacted, 'update')

    def update_render(self, dt):
        pass

    def player_collision(self, player):
        if self.interacted: return#enter only once
        #print(self.interacted, 'col')
        self.player_transport(player)
        player.take_dmg(dmg = 1)
        self.interacted = True

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            self.game_objects.game.state_manager.enter_state(state_name = 'Safe_spawn_1')
            player.currentstate.enter_state('invisible')
        player.velocity = [0,0]
        player.acceleration = [0,0]

    def player_noncollision(self):#when player doesn't collide
        #print(self.interacted, 'non')
        self.interacted = False

class Zoom_col(Interactables):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()
        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 1)
        self.center = kwarg.get('center', (0.5, 0.5))
        self.blur_timer = C.fps

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()

    def player_collision(self, player):
        self.blur_timer -= 1#dt
        if self.blur_timer < 0:
            player.shader_state.handle_input('blur')
            for group in self.game_objects.all_bgs.group_dict.keys():
                for sprite in self.game_objects.all_bgs.group_dict[group]:
                    if sprite.parallax[0] > 0.8:
                        sprite.blur_radius += (1.1/sprite.parallax[0] - sprite.blur_radius) * 0.06
                        sprite.blur_radius = min(1.1/ sprite.parallax[0], sprite.blur_radius)
                    else:
                        sprite.blur_radius -= (sprite.blur_radius - 0.2) * 0.06
                        sprite.blur_radius = max(sprite.blur_radius, 0.2)

        if self.interacted: return
        self.game_objects.camera_manager.zoom(rate = self.rate, scale = self.scale, center = self.center)
        self.interacted = True#sets to false when player gos away

    def player_noncollision(self):#when player doesn't collide: for grass
        self.blur_timer = C.fps
        self.interacted = False
        if self.game_objects.post_process.shaders.get('zoom', False):
            self.game_objects.post_process.shaders['zoom'].method = 'zoom_out'
            self.game_objects.player.shader_state.handle_input('idle')
            for group in self.game_objects.all_bgs.group_dict.keys():
                for sprite in self.game_objects.all_bgs.group_dict[group]:
                    if sprite.parallax[0] == 1: sprite.blur_radius = 0.2
                    else: sprite.blur_radius = min(1/sprite.parallax[0], 10)#limit the blur raidus for performance

class Path_col(Interactables):
    def __init__(self, pos, game_objects, size, destination, spawn):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update_render(self, dt):
        pass

    def update(self, dt):
        pass
        #self.group_distance()

    def player_movement(self, player):#the movement aila does when colliding
        if self.rect[3] > self.rect[2]:#if player was trvelling horizontally, enforce running in that direction
            player.currentstate.enter_state('Run_main')#infstaed of idle, should make her move a little dependeing on the direction
            player.acceleration[0] = C.acceleration[0]
        else:#vertical travelling
            if player.velocity[1] < 0:#up
                player.velocity[1] = -10
            else:#down
                pass

    def player_collision(self, player):
        self.player_movement(player)
        self.game_objects.load_map(self.game_objects.game.state_manager.state_stack[-1], self.destination, self.spawn)#nned to send previous state so that we can update and render for exampe gameplay or title screeen while fading
        self.kill()#so that aila only collides once

class Path_inter(Interactables):
    def __init__(self, pos, game_objects, size, destination, spawn, image, sfx):
        super().__init__(pos, game_objects, sfx)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()

    def update_render(self, dt):
        pass

    def interact(self):
        if self.sfx: self.play_sfx()
        self.game_objects.player.reset_movement()
        self.game_objects.player.currentstate.enter_state('Idle_main')#infstaed of idle, should make her move a little dependeing on the direction
        self.game_objects.load_map(self.game_objects.game.state_manager.state_stack[-1],self.destination, self.spawn)

class Shade_trigger(Interactables):#it changes the colourof shade screen to a new colour specified by self.new_colour
    def __init__(self, pos, game_objects, size, colour = pygame.Color(0,0,0,0)):
        super().__init__(pos, game_objects)
        self.new_colour = [colour.g,colour.b,colour.a]
        self.light_colour = self.game_objects.lights.ambient[0:3]
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self, dt):
        pass

    def player_collision(self, player):#player collision
        self.game_objects.lights.ambient = self.new_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('mix_colour')

    def player_noncollision(self):#when player doesn't collide
        self.game_objects.lights.ambient = self.light_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('idle')

    def add_shade_layers(self, layers):#called from map loader
        self.layers = layers
        for layer in layers:
            layer.new_colour = self.new_colour + [layer.colour[-1]]
            layer.bounds = self.rect

class Interactable_bushes(Interactables):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.interacted = False

    def player_collision(self, player):#player collision
        if self.interacted: return
        self.currentstate.handle_input('Once',animation_name ='hurt', next_state = 'idle')
        self.interacted = True#sets to false when player gos away

    def take_dmg(self,projectile):#when player hits with sword
        self.currentstate.handle_input('Death')

    def reset_timer(self):
        super().reset_timer()
        self.currentstate.handle_input('Idle')

    def player_noncollision(self):#when player doesn't collide
        self.interacted = False

class Cave_grass(Interactable_bushes):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/bushes/cave_grass/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

    def player_collision(self, player):
        if self.interacted: return
        self.currentstate.handle_input('Once',animation_name ='hurt', next_state = 'Idle')
        self.interacted = True#sets to false when player gos away
        self.release_particles()

    def take_dmg(self,projectile):
        super().take_dmg(projectile)
        self.release_particles(3)

    def release_particles(self, number_particles = 12):#should release particles when hurt and death
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Circle')(self.hitbox.center,self.game_objects, distance=30, lifetime=300, vel = {'wave': [3, 14]}, scale=2, fade_scale = 1.5)
            self.game_objects.cosmetics.add(obj1)

class Cocoon(Interactables):#larv cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/cocoon/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.health = 3
        self.flags = {'invincibility': False}

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        #projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.flags['invincibility']  = True

        if self.health > 0:
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.currentstate.handle_input('Once', animation_name = 'hurt', next_state = 'Idle')
            #self.shader_state.handle_input('Hurt')#turn white
        else:#death
            self.currentstate.handle_input('Once', animation_name = 'interact', next_state = 'Interacted')
            self.game_objects.enemies.add(Maggot(self.rect.center,self.game_objects))

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

class Cocoon_boss(Cocoon):#boss cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/cocoon_boss/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.aggro_distance = [200,50]
        self.currentstate = states_cocoon_boss.Idle(self)
        self.item = Tungsten
        self.game_objects.signals.subscribe('who_is_cocoon', self.respond_to_cutscene)#the signal is emitted when the cutscene is initalised

    def respond_to_cutscene(self, callback):
        callback(self)

    def particle_release(self):
        for i in range(0,30):
            obj1 = getattr(particles, 'Circle')(self.rect.center,self.game_objects,distance=0,lifetime=55,vel={'linear':[7,14]},dir='isotropic',scale=0.5,colour = [255,255,255,255])
            self.game_objects.cosmetics.add(obj1)

    def take_dmg(self,projectile):
        if self.flags['invincibility']: return
        self.flags['invincibility'] = True
        self.game_objects.quests_events.initiate_quest('butterfly_encounter')

class Runestones(Interactables):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/runestones/' + ID_key + '/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.true_pos = self.rect.topleft
        self.hitbox.midbottom = self.rect.midbottom

        if state:
            self.currentstate = runestone_states.Interacted(self)
        else:
            self.currentstate = runestone_states.Idle(self)

    def interact(self):
        if type(self.currentstate).__name__ == 'Interacted': return
        self.game_objects.player.currentstate.enter_state('crouch')
        self.currentstate.handle_input('transform')#goes to interacted after transform
        self.game_objects.world_state.state[self.game_objects.map.level_name]['runestone'][self.ID_key] = True#write in the state dict that this has been picked up

class Uber_runestone(Interactables):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/uber_runestone/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.runestone_number = 0#a counter of number of activated runestrones
        self.count_runestones()

    def count_runestones(self):#append all runestone ID that have been activated.
        for level in self.game_objects.world_state.state.keys():
            for runestoneID in self.game_objects.world_state.state[level]['runestone'].keys():
                if self.game_objects.world_state.state[level]['runestone'][runestoneID] != 'idle':
                    pos = [self.rect.x+int(runestoneID)*16,self.rect.y]
                    self.game_objects.cosmetics.add(Rune_symbol(pos,runestoneID))
                    self.runestone_number += 1

    def interact(self):#when player press T
        if self.runestone_number == 25:
            pass#do a cutscene?

class Loot_containers(Interactables):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/loot_containers/' + type(self).__name__.lower() + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

        self.health = 3
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.flags = {'invincibility': False}

        if state:
            self.currentstate = loot_container_states.Interacted(self)
            self.flags['invincibility'] = True
        else:
            self.currentstate = loot_container_states.Idle(self)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop, self.game_objects)#make a class based on the name of the key: need to import sys
                obj.spawn_position()
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def take_dmg(self,projectile):
        if self.flags['invincibility']: return
        self.game_objects.sound.play_sfx(self.sounds['hit'][0], vol = 0.2)
        projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.flags['invincibility'] = True
        self.shader_state.handle_input('Hurt', colour = [1,1,1,1], direction = [1,0.5])
        self.hit_loot()

        if self.health > 0:
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        else:
            self.currentstate.handle_input('open')
            self.game_objects.world_state.state[self.game_objects.map.level_name]['loot_container'][self.ID_key] = True#write in the state dict that this has been picked up

    def hit_loot(self):#sput out amvers when hit
        for i in range(0, random.randint(1,3)):
            obj = Amber_droplet(self.hitbox.midtop, self.game_objects)
            self.game_objects.loot.add(obj)

class Chest(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':3}

class Chest_2(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':1}

    def hit_loot(self):
        pass

class Chest_3(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':3}

    def hit_loot(self):
        pass

class Amber_tree(Loot_containers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/amber_tree/')
        self.inventory = {'Amber_droplet':3}

class Amber_rock(Loot_containers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/amber_rock/')
        self.inventory = {'Amber_droplet':3}

class Door(Interactables):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/door/')
        self.sprites=read_files.load_sprites_dict('assets/sprites/animations/Door/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        self.game_objects.sound.play_sfx(self.sounds['open'][0], vol = 0.2)
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Savepoint(Interactables):#save point
    def __init__(self, pos, game_objects, map):
        super().__init__(pos, game_objects)
        self.sprites=read_files.load_sprites_dict('assets/sprites/animations/savepoint/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]
        self.currentstate = states_savepoint.Idle(self)

    def interact(self):#when player press t/y
        self.game_objects.player.currentstate.enter_state('crouch')
        self.game_objects.player.backpack.map.save_savepoint(map =  self.map, point = self.init_cord)
        self.currentstate.handle_input('active')
        self.game_objects.cosmetics.add(Logo_loading(self.game_objects))

class Inorinoki(Interactables):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/inorinoki/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def interact(self):#when player press t/y
        self.game_objects.game.state_manager.enter_state(state_name = 'Soul_essence', category = 'game_states_facilities')

class Fast_travel(Interactables):
    cost = 50
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/fast_travel/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

        try:#if it has been unlocked
            self.game_objects.world_state.travel_points[map]
            self.locked = False
        except:
            self.locked = True#starts locked. After paying some ambers, it unlocks and fast travel is open

    def unlock(self):#called from Fast_travel_unlock
        if self.game_objects.player.backpack.inventory.get_quantity('amber_droplet') > self.cost:
            self.game_objects.player.backpack.inventory.remove('amber_droplet', self.cost)
            self.locked = False
            Fast_travel.cost *= 5#increase by 5 for every unlock
            self.game_objects.backpack.map.save_travelpoint(self.map,self.init_cord)
            return True
        else:
            return False

    def interact(self):#when player press t/y
        if self.locked:
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_unlock', category = 'game_states_facilities', fast_travel = self)
        else:
            self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_menu', category = 'game_states_facilities')

class Rhoutta_altar(Interactables):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/rhoutta_altar/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
        self.game_objects.game.state_manager.enter_state(state_name = 'Rhoutta_encounter', category = 'cutscenes')

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Light_crystal(Interactables):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/light_crystals/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.flags = {'invincibility': False}

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        projectile.clash_particles(self.hitbox.center)
        self.flags['invincibility'] = True
        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.currentstate.handle_input('Transform')
        self.game_objects.lights.add_light(self)#should be when interacted state is initialised and not on taking dmg

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

class Fireplace(Interactables):
    def __init__(self, pos, game_objects, on = False):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/fireplace/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/fireplace/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom
        self.currentstate = states_fireplace.Idle(self)
        self.light_sources = []#save light references to turn be able to removr them
        if on:
            self.interact()

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Interact')#goes to interacted after transform

    def make_light(self):
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],flicker=True,radius = 100))
        self.light_sources.append(self.game_objects.lights.add_light(self, flicker = True, radius = 50))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],radius = 100))

class Spikes(Interactables):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.dmg = 1

class Spirit_spikes(Interactables):#traps
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/spirit_spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.size = [32,32]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Death')

class Lightning_spikes(Interactables):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/lightning_spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 26, 16)
        self.size = [64,64]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Once')

class Grind(Interactables):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/grind/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_grind.Active(self)#

        self.frequency = int(kwarg.get('frequency', -1))#infinte -> idle - active
        direction = kwarg.get('direction', '0,0')#standing still
        string_list = direction.split(',')
        self.direction = [int(num) for num in string_list]
        self.distance = int(kwarg.get('distance', 1))#standing still
        self.speed = float(kwarg.get('speed', 1))

        self.velocity = [0, 0]
        self.time = 0
        self.original_pos = pos

    def update_vel(self):
        self.velocity[0] = self.direction[0] * self.distance * math.cos(self.speed * self.time)
        self.velocity[1] = self.direction[1] * self.distance * math.sin(self.speed * self.time)

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.currentstate.update()
        self.update_vel()
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.original_pos[0] + self.velocity[0] * dt,self.original_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos
        self.hitbox.center = self.rect.center

    def group_distance(self):
        pass

    def player_collision(self, player):#player collision
        player.take_dmg(dmg = 1)

    def take_dmg(self, projectile):#when player hits with e.g. sword
        if hasattr(projectile, 'sword_jump'):#if it has the attribute
            projectile.sword_jump()

class Door_inter(Interactables): #game object for itneracting with locked door
    def __init__(self, pos, game_objects, door_obj):
        super().__init__(pos, game_objects)
        self.door = door_obj
        self.rect = door_obj.rect.copy()
        self.rect = self.rect.inflate(5,0)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        if type(self.door.currentstate).__name__ == 'Erect':
            if self.game_objects.player.backpack.inventory.get_quantity(self.door.key):
                self.door.currentstate.handle_input('Transform')
                if self.sfx: self.play_sfx()
            else:
                self.door.shake()

    def player_collision(self, player):#player collision
        pass

    def update(self, dt):
        pass

    def draw(self, target):
        pass

    def release_texture(self):
        pass

class Lever(Interactables):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/lever/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.references = []

        self.ID_key = kwarg.get('ID', None)#an ID to match with the reference (gate or platform etc) and an unique ID key to identify which item that the player is intracting within the world
        self.flags = {'invincibility': False}
        if self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'].get(self.ID_key, False) or kwarg.get('on', False):
            self.currentstate = states_lever.On(self)
        else:
            self.currentstate = states_lever.Off(self)

        self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = kwarg.get('on', False)

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        self.flags['invincibility'] = True
        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while

        projectile.clash_particles(self.hitbox.center)

        self.currentstate.handle_input('Transform')
        self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = not self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key]#write in the state dict that this has been picked up

        for reference in self.references:
            reference.currentstate.handle_input('Transform')

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def add_reference(self, reference):#called from map loader
        self.references.append(reference)

class Shadow_light_lantern(Interactables):#emits a shadow light upon interaction. Shadow light inetracts with dark forest enemy and platofrm
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/shadow_light_lantern/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.light_sources = []
        if kwarg.get('on', False):
            self.make_light()

    def interact(self):#when player press t/y
        if not self.light_sources:
            self.make_light()
        else:
            for light in self.light_sources:
                self.game_objects.lights.remove_light(light)
            self.light_sources = []

    def make_light(self):
        self.light_sources.append(self.game_objects.lights.add_light(self, shadow_interact = False, colour = [100/255,175/255,255/255,255/255],flicker=True,radius = 300))
        self.light_sources.append(self.game_objects.lights.add_light(self, radius = 250, colour = [100/255,175/255,255/255,255/255],flicker=True))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [100/255,175/255,255/255,255/255],radius = 200))


#shader absed
class Portal_2(StaticEntity):#same as portal but masked based. Doesnt work becasue the mask is repeated for some reason
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.mask_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 0.4#one is screen size

        self.state = kwarg.get('state', None)

        game_objects.interactables.add(Place_holder_interacatble(self, game_objects))#add a dummy interactable to the group, since portal cannot be in inetracatles
        game_objects.render_state.handle_input('portal', portal = self)

    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.bg_grey_layer.release()
        self.bg_distort_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self, dt):
        self.currentstate.update()#handles the radius and thickness of portal
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #mask
        self.game_objects.shaders['circle_pos']['radius'] = self.radius
        self.game_objects.shaders['circle_pos']['color'] = [255,255,255,255]
        self.game_objects.shaders['circle_pos']['gradient'] = 1
        self.game_objects.game.display.render(self.empty_layer.texture, self.mask_layer, shader = self.game_objects.shaders['circle_pos'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort_2']['TIME'] = self.time
        self.game_objects.shaders['distort_2']['maskTexture'] = self.mask_layer.texture
        self.game_objects.shaders['distort_2']['center'] = blit_pos
        self.game_objects.shaders['distort_2']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort_2']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort_2'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['distort_2'])#make them gre

class Portal(StaticEntity):#portal to make a small spirit world with challenge rooms
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 1#one is screen size

        self.state = kwarg.get('state', None)

        game_objects.interactables.add(Place_holder_interacatble(self, game_objects))#add a dummy interactable to the group, since portal cannot be in inetracatles
        game_objects.render_state.handle_input('portal', portal = self)

    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.bg_grey_layer.release()
        self.bg_distort_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self, dt):
        self.currentstate.update()#handles the radius and thickness of portal
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort']['TIME'] = self.time
        self.game_objects.shaders['distort']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['distort']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort']['center'] = [self.rect.center[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.center[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['distort']['radius'] = self.radius
        self.game_objects.shaders['distort']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.empty_layer, shader = self.game_objects.shaders['distort'])#make them grey
        self.game_objects.shaders['edge_light']['TIME'] = self.time
        self.game_objects.shaders['edge_light']['textureNoise'] = self.noise_layer.texture
        self.game_objects.game.display.render(self.empty_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['edge_light'])#make them grey

#platforms? -> if non collision is needed, then interactable
class Lighitning(StaticEntity):#a shader to make lighning barrier
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.parallax = parallax

        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['lightning']['TIME'] = self.time
        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['lightning'])

    def player_collision(self):#player collision
        pm_one = sign(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        self.game_objects.player.take_dmg(dmg = 1, effects = [lambda: self.game_objects.player.knock_back(amp = [50, 0], dir = [pm_one, 0])])
        self.game_objects.player.currentstate.handle_input('interrupt')#interupts dash

    def player_noncollision(self):
        pass

#platforms?
class Bubble_gate(StaticEntity):#a shader to make bubble barrier
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.image = self.game_objects.game.display.make_layer(size).texture#TODO
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def player_noncollision(self):
        pass

    def player_collision(self):
        self.game_objects.player.velocity[0] += (self.game_objects.player.hitbox.centerx - self.hitbox.centerx)*0.02

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['bubbles']['TIME'] = self.time
        pos =  (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.game_objects.shaders['bubbles'])#int seem nicer than round

    def release_texture(self):#called when .kill() and empty group
        self.image.release()        

class Up_stream(StaticEntity):#a draft that can lift enteties along a direction
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.hitbox = pygame.Rect(pos[0] + size[0]* 0.05, pos[1], size[0] * 0.9, size[1])#adjust the hitbox size based on texture
        self.time = 0
        self.accel_y = 0.8
        self.accel_x = 0.8
        self.max_speed = 7

        horizontal = kwarg.get('horizontal', 0)
        vertical = kwarg.get('vertical', 0)
        normalise = (horizontal**2 + vertical**2)**0.5
        self.dir = [horizontal/normalise, vertical/normalise]

        sounds = read_files.load_sounds_dict('assets/audio/sfx/environment/up_stream/')
        self.channel = game_objects.sound.play_sfx(sounds['idle'][0], loop = -1, vol = 0.5)
        self.interacted = False#for player collision

    def player_collision(self, player):#player collision
        if self.interacted: return
        self.interacted = True
        if self.dir[0] != 0:
            player.movement_manager.add_modifier('up_stream_horizontal', speed = [self.dir[0] * self.accel_x, self.dir[1] * self.accel_y])
        elif self.dir[1] != 0:
            player.movement_manager.add_modifier('up_stream_vertical', speed = [self.dir[0] * self.accel_x, self.dir[1] * self.accel_y])#add modifier to player movement manager

        #context = player.movement_manager.resolve()
        #player.velocity[0] += self.dir[0] * self.accel_x * context.upstream
        #player.velocity[1] += self.dir[1] * self.accel_y * context.upstream + self.dir[1] * int(player.collision_types['bottom'])#a small inital boost if on ground
        #if (player.velocity[1]) < 0:
        #    player.velocity[1] = min(abs(player.velocity[1]), self.max_speed) * self.dir[1]

    def player_noncollision(self):
        if not self.interacted: return
        if self.dir[0] != 0:
            self.game_objects.player.movement_manager.remove_modifier('up_stream_horizontal')
        elif self.dir[1] != 0:
            self.game_objects.player.movement_manager.remove_modifier('up_stream_vertical')

        self.interacted = False

    def release_texture(self):
        self.image.release()
        self.channel.fadeout(300)

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render        

class TwoD_liquid(StaticEntity):#inside interactables_fg group. fg because in front of player
    def __init__(self, pos, game_objects, size, layer_name, **properties):
        super().__init__(pos, game_objects)
        self.empty = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
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
                self.currentstate = states_twoD_liquid.Poison(self, **properties)
            else:#vertical scroller -> golden fields
                self.currentstate = states_twoD_liquid.Poison_vertical(self, **properties)
        else:
            self.currentstate = states_twoD_liquid.Water(self, **properties)

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

    def player_collision(self, player):#player collision
        if self.interacted: return
        player.movement_manager.add_modifier('TwoD_liquid')
        vel_scale = player.velocity[1] / C.max_vel[1]
        self.splash(player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [7 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        player.timer_jobs['wet'].deactivate()#stop dropping if inside the water again
        self.interacted = True
        self.currentstate.player_collision(player)

    def player_noncollision(self):
        if not self.interacted: return
        self.game_objects.player.movement_manager.remove_modifier('TwoD_liquid')
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