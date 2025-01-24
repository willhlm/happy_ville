import pygame
import entities, states_time_collision, animation, read_files, states_basic, states_gate, states_smacker, states_moving_platform, states_shader
import constants as C

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self, pos, size = (16,16), run_particle = 'dust'):
        super().__init__()
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()
        #self.run_particles = {'dust':entities.Dust_running_particles,'water':entities.Water_running_particles,'grass':entities.Grass_running_particles}[run_particle]

    def collide_x(self, entity):
        pass

    def collide_y(self, entity):
        pass

    def draw(self, target):#conly certain platforms will require draw
        pass

    def take_dmg(self, projectile):#called from projectile
        pass

    def release_texture(self):#called when .kill() and empty group
        pass

    def kill(self):
        self.release_texture()#before killing, need to release the textures (but not the onces who has a pool)
        super().kill()

    def jumped(self):#called from player states jump_main
        return C.air_timer

class Collision_block(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size, run_particle)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

class Collision_oneway_up(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size, run_particle)

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] < 0: return#going up
        offset = entity.velocity[1] + abs(entity.velocity[0]) + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            entity.down_collision(self)
            entity.limit_y()
            entity.update_rect_y()

class Collision_right_angle(Platform):#ramp
    def __init__(self, pos, points, go_through = True):
        self.define_values(pos, points)
        super().__init__([self.new_pos[0],self.new_pos[1]-self.size[1]],self.size)
        self.ratio = self.size[1]/self.size[0]
        self.go_through = go_through#a flag that determines if aila can go through when pressing down
        self.target = 0
    #function calculates size, real bottomleft position and orientation of right angle triangle
    #the value in orientatiion represents the following:
    #0 = tilting to the right, flatside down
    #1 = tilting to the left, flatside down
    #2 = tilting to the right, flatside up
    #3 = tilting to the left, flatside up

    def define_values(self, pos, points):
        self.new_pos = (0,0)
        self.size = (0,0)
        self.orientation = 0
        x_0_count = 0
        y_0_count = 0
        x_extreme = 0
        y_extreme = 0

        for point in points:
            if point[0] == 0:
                x_0_count += 1
            else:
                x_extreme = point[0]
            if point[1] == 0:
                y_0_count += 1
            else:
                y_extreme = point[1]

        self.size = (abs(x_extreme), abs(y_extreme))

        if x_extreme < 0:
            if y_extreme < 0:
                self.new_pos = (pos[0] + x_extreme, pos[1])
                if x_0_count == 1:
                    self.orientation = 0
                elif y_0_count == 1:
                    self.orientation = 3
                else:
                    self.orientation = 1

            else:
                self.new_pos = (pos[0] + x_extreme, pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 2
                elif y_0_count == 1:
                    self.orientation = 1
                else:
                    self.orientation = 3

        else:
            if y_extreme < 0:
                self.new_pos = pos
                if x_0_count == 1:
                    self.orientation = 1
                elif y_0_count == 1:
                    self.orientation = 2
                else:
                    self.orientation = 0

            else:
                self.new_pos = (pos[0], pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 3
                elif y_0_count == 1:
                    self.orientation = 0
                else:
                    self.orientation = 2

    def get_target(self,entity):#called when oresing down
        if self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
        elif self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
        else: return 0
        return -rel_x*self.ratio + self.hitbox.bottom

    def collide(self, entity):#called in collisions
        if self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
            other_side = self.hitbox.left - entity.hitbox.left
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom
            self.shift_up(other_side, entity, benethe)
        elif self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
            other_side = entity.hitbox.right - self.hitbox.right
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom
            self.shift_up(other_side, entity, benethe)
        elif self.orientation == 2:
            rel_x = self.hitbox.right - entity.hitbox.left
            self.target = rel_x*self.ratio + self.hitbox.top
            self.shift_down(entity)
        else:#orientation 3
            rel_x = entity.hitbox.right - self.hitbox.left
            self.target = rel_x*self.ratio + self.hitbox.top
            self.shift_down(entity)

    def shift_down(self,entity):
        if entity.hitbox.top < self.target:
            entity.ramp_top_collision(self.target)
            entity.update_rect_y()

    def shift_up(self, other_side, entity, benethe):
        if self.target > entity.hitbox.bottom:
            entity.go_through['ramp'] = False
        elif other_side > 0 or benethe > 0:
            entity.go_through['ramp'] = True
        elif not entity.go_through['ramp']: #need to be elif
            entity.ramp_down_collision(self.target)
            entity.update_rect_y()

class Collision_dmg(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.dmg = 1

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self)
            entity.velocity[0] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self)
            entity.velocity[1] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_y()

#texture based
class Collision_texture(Platform):#blocks that has tectures
    def __init__(self, pos, game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.dir = [1,0]#states need it

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def reset_timer(self):#aniamtion need it
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])))#int seem nicer than round

class Boulder(Collision_texture):#blocks village cave
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/boulder/', game_objects)

        if game_objects.world_state.events.get('reindeer', False):#if reindeer has been deafeated
            state = 'down'
        else:
            state = 'erect'

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

class Gate_1(Collision_texture):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.init()

        self.ID_key = kwarg.get('ID', 'None')#an ID to match with the gate
        if game_objects.world_state.quests.get(self.ID_key[:self.ID_key.rfind('_')], False):#if quest accodicated with it has been completed
            state = 'down'
        elif game_objects.world_state.events.get(self.ID_key[:self.ID_key.rfind('_')], False):#if the event has been completed
            state = 'down'
        else:
            state = {True: 'erect', False: 'down'}[kwarg.get('erect', False)]#a flag that can be specified in titled
        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)#hitbox is set in state

        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/gates/gate_1/', self.game_objects)

class Gate_2(Gate_1):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/gates/gate_2/', self.game_objects)

class Door(Gate_1):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        #self.sfx = ADDSFXHERE
        self.key = kwarg.get('key', 'None')
        self.shader = None
        self.shader_state = states_shader.Idle(self)

    def update(self):
        super().update()
        self.shader_state.update()

    def draw(self, target):
        self.shader_state.draw()
        self.game_objects.game.display.render(self.image, target, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])), shader = self.shader)#int seem nicer than round

    def shake(self):
        self.shader_state.handle_input('Hurt', colour = (1,1,1,0))

class Door_right_orient(Door):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.shader_state = states_shader.Idle(self)
        self.hitbox[2] = self.hitbox[2] - 8
        self.hitbox.bottomright = self.rect.bottomright

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/door_right/', self.game_objects)

class Door_left_orient(Door):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.shader_state = states_shader.Idle(self)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/door_left/', self.game_objects)

class Bridge(Collision_texture):#bridge twoards forest path
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/bridge/', game_objects)

        if game_objects.world_state.events.get('reindeer', False):#if reindeer has been deafeated
            state = 'erect'
        else:
            state = 'down'

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

class Conveyor_belt(Collision_texture):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.tile_size = [16,16]

        if kwarg.get('vertical', False):#default is horizontal belft
            angle = 90
            size[1] = max(size[1], self.tile_size[1] * 3)#assert at least 3 tiles
            if kwarg.get('up', False):#default is up down betls
                self.direction = [0, -1]
            else:#down
                self.direction = [0, 1]
            animation_direction =  self.direction[1]
        else:#horizontal
            angle = 0
            size[0] = max(size[0], self.tile_size[0] * 3)#assert at least 3 tiles
            if kwarg.get('right', False):#default is left moving belts
                self.direction = [1,0]
            else:#left
                self.direction = [-1, 0]
            animation_direction =  -self.direction[0]

        self.make_belt(size, angle)
        self.animation = animation.Animation(self, direction = animation_direction)#can revert the animation direction
        self.currentstate = states_basic.Idle(self)

        self.rect = pygame.Rect(pos, size)
        self.true_pos = list(self.rect.topleft)
        if angle == 0:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2] - 16), self.rect[3] * 0.55)
        else:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2]) * 0.55, (self.rect[3]-16))
        self.hitbox.center = self.rect.center

    def make_belt(self, size, angle = 0):#the spits are divided into left, middle and right. Merge them here
        sprites = read_files.load_sprites_dict('Sprites/block/conveyor_belt/', self.game_objects)

        self.sprites = {'idle' : []}
        self.layers = []#store each layer so that it can be released
        principle_sections = ['left', 'middle','right']#the middle will be placed multiple times depending on the size

        if angle == 0:
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[0]/self.tile_size[0]) - 2) + [principle_sections[2]]
        else:#90
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[1]/self.tile_size[1]) - 2) + [principle_sections[2]]

        for frame in range(0, len(sprites[sections[0]]) - 1):
            self.layers.append(self.game_objects.game.display.make_layer(size))
            for index, section in enumerate(sections):
                if angle == 0:
                    pos = [sprites[sections[index - 1]][frame].width * index , 0]
                else:#vertical
                    pos = [0, sprites[sections[index - 1]][frame].height * index ]

                self.game_objects.game.display.render(sprites[section][frame], self.layers[-1], position = pos, angle = angle)#int seem nicer than round

            self.sprites['idle'].append(self.layers[-1].texture)
        self.image =  self.sprites['idle'][0]

        for state in sprites.keys():
            for frame in range(0,len(sprites[state])):
                sprites[state][frame].release()

    def release_texture(self):
        super().release_texture()
        for layer in self.layers:
            layer.release()

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self, 'belt')
            entity.velocity[1] += self.game_objects.game.dt * self.direction[1]
        else:#going to the leftx
            entity.left_collision(self, 'belt')
            entity.velocity[1] += self.game_objects.game.dt * -self.direction[1]
        entity.update_rect_x()

    def collide_y(self,entity):
        super().collide_y(entity)
        entity.velocity[0] += self.game_objects.game.dt * self.direction[0] * 0.1
        entity.friction[0] = C.friction_player[0] - 0.1 * self.direction[0] * entity.dir[0]
        entity.timer_jobs['friction'].activate()

#shadow light platforms: platforms that appear under shadow light
class Shadow_light(Collision_texture):#parent class: add the subclasses to cosmetics group
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.platforms = []#keep diffeernt collision blocks to dynamically change the size

    def check_light(self):
        new_platforms = []
        for light in self.game_objects.lights.lights_sources:
            #if not light.shadow_light: continue
            if not self.hitbox.colliderect(light.hitbox): continue

            overlap_rect = self.hitbox.clip(light.hitbox)
            if len(new_platforms) < len(self.platforms):
                platform = self.platforms[len(new_platforms)]
                platform.hitbox = overlap_rect
                platform.rect = overlap_rect
            else:
                platform = Collision_block(overlap_rect.topleft, size=[overlap_rect.width, overlap_rect.height])
                self.game_objects.platforms.add(platform)

            new_platforms.append(platform)

        for platform in self.platforms[len(new_platforms):]:# Remove platforms that are no longer active
            self.game_objects.platforms.remove(platform)

        self.platforms = new_platforms# Update the platforms list

    def draw(self, target):
        #copy the light texture
        blit_pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.cut_rect.topleft = blit_pos
        self.game_objects.game.display.render(self.game_objects.lights.layer3.texture, self.lights, flip = [False, True], section = self.cut_rect, shader = self.game_objects.shaders['reverse_y'])#cut out the light texture

        #blend
        self.game_objects.shaders['blend_shadow_light']['platform'] = self.image
        self.game_objects.game.display.render(self.lights.texture, target, position = blit_pos, shader = self.game_objects.shaders['blend_shadow_light'])#blend light and rectangle

    def release_texture(self):#called when .kill() and empty group
        super().release_texture()
        self.platforms = []
        self.lights.release()

class Collision_shadow_light(Shadow_light):#collsion block but only lights and interacts when there is light overlap
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.size = size

        self.empty = game_objects.game.display.make_layer(size)
        self.image_layer = game_objects.game.display.make_layer(size)
        self.lights = game_objects.game.display.make_layer(size)

        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.cut_rect = self.rect.copy()  # A rectangle used to cut out light sources for shader
        self.hitbox = self.rect.copy()  # The initial hitbox of the platform
        self.time = 0

        self.game_objects.shaders['rectangle_border']['screenSize'] = self.game_objects.game.window_size

    def update(self):
        self.check_light()  # Check if the platform is hit by light
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['rectangle_border']['TIME'] = self.time
        self.game_objects.game.display.render(self.empty.texture, self.image_layer, shader=self.game_objects.shaders['rectangle_border'])#make the rectangle
        self.image = self.image_layer.texture
        super().draw(target)

    def release_texture(self):#called when .kill() and empty group
        self.image.release()
        self.image_layer.release()
        self.empty.release()
        self.lights.release()
        self.platforms = []

class Dark_forest_1(Shadow_light):#a platform which dissapears when there is no light
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/light_interaction/dark_forest_1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.cut_rect = pygame.Rect(pos[0], pos[1], self.image.size[0], self.image.size[1])
        self.lights = game_objects.game.display.make_layer(self.image.size)

    def update(self):
        self.check_light()

#timer based
class Collision_timer(Collision_texture):#collision block that dissapears if aila stands on it
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_time_collision.Idle(self)#

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):#called when aila lands on platoform
        if entity.velocity[1] < 0: return#going up
        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            self.game_objects.timer_manager.start_timer(60, self.deactivate)
            entity.down_collision(self)
            entity.limit_y()
            entity.update_rect_y()

class Rhoutta_encounter_1(Collision_timer):
    def __init__(self, game_objects, pos, particle):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/rhoutta_encounter_1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()

    def deactivate(self):#called when timer_disappear runs out
        self.hitbox = [self.hitbox[0], self.hitbox[1], 0, 0]
        self.game_objects.timer_manager.start_timer(60, self.activate)
        self.currentstate.handle_input('Transition_1')

    def activate(self):#called when timer_appear runs out
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

class Crystal_mines_1(Collision_timer):
    def __init__(self, game_objects, pos):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/crystal_mines_1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = pygame.Rect(pos[0], pos[1], self.rect[2], self.rect[3]*0.4)
        self.hitbox.center = self.rect.center

    def deactivate(self):#called when timer_disappear runs out
        self.hitbox[2], self.hitbox[3] = 0, 0
        self.game_objects.timer_manager.start_timer(60, self.activate)
        self.currentstate.handle_input('Transition_1')

    def activate(self):#called when timer_appear runs out
        self.hitbox[2], self.hitbox[3] = self.rect[2], self.rect[3]*0.4
        self.currentstate.handle_input('Transition_2')

class Bubble_static(Collision_timer):#static bubble
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/bubble/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.lifetime = prop.get('lifetime', 100)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            self.game_objects.timer_manager.start_timer(self.lifetime, self.deactivate)
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def deactivate(self):#called when first timer runs out
        self.hitbox = [self.hitbox[0],self.hitbox[1],0,0]
        self.game_objects.timer_manager.start_timer(self.lifetime, self.activate)
        self.currentstate.handle_input('Transition_1')

    def activate(self):
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

#breakable
class Collision_breakable(Collision_texture):#breakable collision blocks
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.flags = {'invincibility': False}
        self.health = 3
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def dead(self):#called when death animatin finishes
        self.kill()

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        self.health -= projectile.dmg
        self.flags['invincibility'] = True

        self.game_objects.camera_manager.camera_shake(amplitude = 3, duration = 10)

        if self.health > 0:#check if dead¨
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            #turn white TODO
        else:#if dead
            self.currentstate.enter_state('Death')#overrite any state and go to deat

class Breakable_block_1(Collision_breakable):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/breakable/light_forest/type1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

class Breakable_block_charge_1(Collision_breakable):#only projectiles that has 'charge' can break these blocks
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/breakable/charge_blocks/type1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.health = 3

    def take_dmg(self, projectile):
        if not projectile.flags['charge_blocks']: return
        super().take_dmg(projectile)

#one side breakble collision
class Collision_breakable_oneside(Collision_breakable):
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.ID_key = ID

    def kill(self):#called when death animatin finishes
        super().kill()
        self.game_objects.world_state.state[self.game_objects.map.level_name]['breakable_platform'][self.ID_key] = True#write in the

class Breakable_oneside_1(Collision_breakable_oneside):
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects, ID)
        self.sprites = read_files.load_sprites_dict('Sprites/block/breakable/light_forest/type2/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

    def take_dmg(self, projectile):
        if projectile.rect.centerx - self.hitbox.centerx > 0:#projectile from right: depends on the speciic objects
            super().take_dmg(projectile)

#dynamics (moving) ones
class Collision_dynamic(Collision_texture):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.velocity = [0,0]

    def update(self):
        super().update()
        self.old_hitbox = self.hitbox.copy()#save old position before moving
        self.update_vel()
        self.update_true_pos_x()
        self.update_true_pos_y()

    def update_true_pos_x(self):
        self.true_pos[0] += self.game_objects.game.dt*self.velocity[0]
        self.rect.left = int(self.true_pos[0])#should be int
        self.hitbox.left = self.rect.left

    def update_true_pos_y(self):
        self.true_pos[1] += self.game_objects.game.dt*self.velocity[1]
        self.rect.top = int(self.true_pos[1])#should be int
        self.hitbox.top = self.rect.top

    def collide_x(self, entity):  # Handles horizontal collision
        if entity.hitbox.right >= self.hitbox.left and entity.old_hitbox.right <= self.old_hitbox.left:
            entity.right_collision(self)
        if entity.hitbox.left <= self.hitbox.right and entity.old_hitbox.left >= self.old_hitbox.right:
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self, entity):  # Handles vertical collision
        if entity.hitbox.bottom >= self.hitbox.top and entity.old_hitbox.bottom <= self.old_hitbox.top:
            entity.down_collision(self)
            entity.limit_y()
            #self.velocity[1] = 1
            self.collided = True

        if entity.hitbox.top <= self.hitbox.bottom and entity.old_hitbox.top >= self.old_hitbox.bottom:
            entity.top_collision(self)
        entity.update_rect_y()  # Update player’s vertical position

class Bubble(Collision_dynamic):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = Bubble.sprites
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()
        self.max_down_vel = 0.6
        self.max_up_vel = -1.3
        self.accel = 3
        self.collided = False

        lifetime = 1000#prop.get('lifetime', 300)
        self.game_objects.timer_manager.start_timer(lifetime, self.deactivate)
        #TODO horitoxntal or veritcal moment
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_time_collision.Idle(self)#s
        self.sign = 1

    def jumped(self):#called from player states jump_main
        self.deactivate()
        scale = self.game_objects.player.player_modifier.bubble_jump()
        return C.air_timer * scale

    def update_vel(self):
        if self.collided:
            self.sign = -1
            self.accel = 40
            self.velocity[1] -= self.sign * self.accel * self.game_objects.game.dt*0.01
            self.velocity[1] = min(self.velocity[1], self.max_down_vel)
        else:
            self.velocity[1] -= self.sign * self.accel * self.game_objects.game.dt*0.01
            self.velocity[1] = max(self.velocity[1], self.max_up_vel)

    def release_texture(self):
        pass

    def pool(game_objects):#all things that should be saved in object pool
        Bubble.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/bubble/', game_objects)

    def deactivate(self):#called when first timer runs out
        self.kill()

class Dark_forest_2(Collision_dynamic):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/moving_platform/dark_forest_2/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.ID_key = prop.get('ID', None)

        self.animation = animation.Animation(self)
        self.currentstate = states_moving_platform.Off(self)#

    def update_vel(self):
        pass

class Smacker(Collision_dynamic):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/smacker/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.hole = kwarg.get('hole', None)

        self.frequency = int(kwarg.get('frequency', 100))#infinte -> idle - active
        self.distance = kwarg.get('distance', 4*16)
        self.original_pos = pos

        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_smacker.Idle(self)

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def collide_entity_y(self,entity):#plpaotfrom mobings
        self.currentstate.collide_entity_y(entity)

    def collide_y(self,entity):#entity moving
        self.currentstate.collide_y(entity)
