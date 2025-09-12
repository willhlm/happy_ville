import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.base.boss import Boss
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.states import states_bird

class Flower_butterfly(FlyingEnemy):#peaceful ones
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/flower_butterfly/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/flower_butterfly/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1
        self.aggro_distance = [0,0]
        self.game_objects.lights.add_light(self, colour = [77/255,168/255,177/255,200/255], interact = False)
        self.flags['aggro'] = False

    def update(self, dt):
        super().update(dt)
        obj1 = particles.Floaty_particles(self.rect.center, self.game_objects, distance = 0, vel = {'linear':[0.1,-1]}, dir = 'isotropic')
        self.game_objects.cosmetics2.add(obj1)

class Mygga(FlyingEnemy):#a non aggro mygga that roams around
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.aggro_distance = [0, 0]

class Mygga_chase(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.aggro_distance = [130, 80]
        self.accel = [0.013, 0.008]
        self.accel_chase = [0.026, 0.009]
        self.deaccel_knock = 0.84
        self.max_chase_vel = 1.8
        self.max_patrol_vel = 1.2
        self.friction = [0.009,0.009]

    def knock_back(self, amp, dir):
        self.currentstate.enter_state('Knock_back')
        amp = 19
        if dir[1] != 0:
            self.velocity[1] = -dir[1] * amp
        else:
            self.velocity[0] = dir[0] * amp

    def player_collision(self, player):#when player collides with enemy
        super().player_collision(player)
        self.velocity = [0, 0]
        self.currentstate.enter_state('Wait', time = 30, next_AI = 'Chase')

    def patrol(self, position):#called from state: when patroling
        self.velocity[0] += sign(position[0] - self.rect.centerx) * self.accel[0]
        self.velocity[1] += sign(position[1] - self.rect.centery) * self.accel[1]
        self.velocity[0] = min(self.max_chase_vel, self.velocity[0])
        self.velocity[1] = min(self.max_chase_vel, self.velocity[1])

    def chase(self, target_distance):#called from state: when chaising
        self.velocity[0] += sign(target_distance[0]) * self.accel_chase[0]
        self.velocity[1] += sign(target_distance[1]) * self.accel_chase[1]
        for i in range(2):
            if abs(self.velocity[i]) > self.max_chase_vel:
                self.velocity[i] = sign(self.velocity[i]) *  self.max_chase_vel

    def chase_knock_back(self, target_distance):#called from state: when chaising
        self.velocity[0] *= self.deaccel_knock#sign(target_distance[0])
        self.velocity[1] *= self.deaccel_knock#sign(target_distance[1])

    def sway(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.008)
        self.velocity[1] += amp*math.sin(2.2*time)# - self.entity.dir[1]*0.1

class Mygga_torpedo(FlyingEnemy):#torpedo
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga_torpedo/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 30

        self.aggro_distance = [180,130]
        self.attack_distance = [150,100]

        self.accel = [0.013, 0.008]
        self.accel_chase = [0.026, 0.009]
        self.deaccel_knock = 0.88
        self.max_chase_vel = 1.8
        self.max_patrol_vel = 1.2
        self.friction = [0.009,0.009]

    def knock_back(self, amp, dir):
        self.currentstate.enter_state('Knock_back')
        amp = [16,16]
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]

    def player_collision(self, player):#when player collides with enemy
        super().player_collision(player)
        self.velocity = [0, 0]
        self.currentstate.enter_state('Wait', time = 30, next_AI = 'Chase')

    def patrol(self, position):#called from state: when patroling
        self.velocity[0] += sign(position[0] - self.rect.centerx) * self.accel[0]
        self.velocity[1] += sign(position[1] - self.rect.centery) * self.accel[1]
        self.velocity[0] = min(self.max_chase_vel, self.velocity[0])
        self.velocity[1] = min(self.max_chase_vel, self.velocity[1])

    def chase(self, target_distance):#called from state: when chaising
        self.velocity[0] += sign(target_distance[0]) * self.accel_chase[0]
        self.velocity[1] += sign(target_distance[1]) * self.accel_chase[1]
        for i in range(2):
            if abs(self.velocity[i]) > self.max_chase_vel:
                self.velocity[i] = sign(self.velocity[i]) *  self.max_chase_vel

    def chase_knock_back(self, target_distance):#called from state: when chaising
        self.velocity[0] *= self.deaccel_knock#sign(target_distance[0])
        self.velocity[1] *= self.deaccel_knock#sign(target_distance[1])

    def sway(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.008)
        self.velocity[1] += amp*math.sin(2.2*time)# - self.entity.dir[1]*0.1

class Mygga_suicide(FlyingEnemy):#torpedo and explode
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga_torpedo/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1

        self.aggro_distance = [180,130]
        self.attack_distance = self.aggro_distance.copy()

    def chase(self, position = [0,0]):#called from AI: when chaising
        pass

    def patrol(self, position = [0,0]):#called from AI: when patroling
        pass

    def player_collision(self, player):#when player collides with enemy
        self.suicide()

    def killed(self):#called when death animation starts playing
        self.suicide()

    def suicide(self):#called from states
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

    #pltform collisions.
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def down_collision(self, block):
        super().down_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def top_collision(self, block):
        super().top_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        super().ramp_down_collision(ramp)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        super().ramp_top_collision(ramp)
        self.currentstate.handle_input('collision')#for suicide

class Mygga_colliding(FlyingEnemy):#bounce around
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.velocity = [random.randint(-2,2),random.randint(-2,2)]
        self.dir[0] = sign(self.velocity[0])
        self.aggro_distance = [0, 0]

    def sway(self, time):#called from walk state
        pass

    def patrol(self, target):
        pass

    def update_vel(self):
        pass

    #ramp collisions
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.velocity[1] *= -1

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

    #platform collision
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = -1

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = 1

    def down_collision(self, block):
        super().down_collision(block)
        self.velocity[1] *= -1

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] *= -1

class Mygga_collising_projectile(Mygga_colliding):#bounce around and eject projectiles
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.currentstate.enter_state('Roaming_attack', frequency = 100)

    def attack(self):#called from roaming AI
        dirs = [[1,1],[-1,1],[1,-1],[-1,-1]]
        for direction in dirs:
            obj = Projectile_1(self.hitbox.center, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

class Mygga_exploding(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga_exploding/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/exploding_mygga/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 4
        self.attack_distance = [70,70]
        self.aggro_distance = [150,100]
        self.currentstate = states_exploding_mygga.Patrol(self)

    def killed(self):
        self.game_objects.sound.play_sfx(self.sounds['explosion'][0], vol = 0.2)
        self.projectiles.add(Hurt_box(self, size = [64,64], lifetime = 30, dir = [0,0]))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

class Mygga_crystal(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/mygga_crystal/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3

        self.currentstate = states_mygga_crystal.Patrol(self)

        self.flee_distance = [50, 50]#starting fleeing if too close
        self.attack_distance = [100, 100]#attack distance
        self.aggro_distance = [150, 100]#start chasing

    def attack(self):#called from state
        dirs = [[1,1], [-1,1], [1,-1], [-1,-1]]
        for direction in dirs:
            obj = Poisonblobb(self.hitbox.topleft, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

    def chase(self, direction):#called from state: when chaising
        self.velocity[0] += direction[0]*0.5
        self.velocity[1] += direction[1]*0.5

    def patrol(self, position):#called from state: when patroling
        self.velocity[0] += (position[0]-self.rect.centerx) * 0.002
        self.velocity[1] += (position[1]-self.rect.centery) * 0.002

class Crab_crystal(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/crab_crystal/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 16, 16)

        self.currentstate = states_crab_crystal.Idle(self)

        self.hide_distance = [100, 50]#the distance to hide
        self.fly_distance = [150, 50]#the distance to hide
        self.attack_distance = [250, 50]
        self.aggro_distance = [300, 50]

    def chase(self, dir = 1):#called from AI: when chaising
        self.velocity[0] += dir*0.6

    def take_dmg(self,dmg):
        return self.currentstate.take_dmg(dmg)

    def attack(self):#called from currenrstate
        for i in range(0, 3):
            vel = random.randint(-3,3)
            new_projectile = Poisonblobb(self.rect.midtop, self.game_objects, dir = [1, -1], amp = [vel, 4])
            self.game_objects.eprojectiles.add(new_projectile)

class Froggy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/froggy/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health = 1
        self.flags['aggro'] = False
        self.attack_distance = [150,50]

        self.currentstate = states_froggy.Idle(self)
        self.inventory = {'Amber_droplet':random.randint(5,15)}#thigs to drop wgen killed

    def knock_back(self,dir):
        pass

class Packun(Enemy):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/packun/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.health = 3

        self.currentstate = packun_states.Idle(self)
        self.angle_state = getattr(packun_states, kwarg['direction'])(self)

    def knock_back(self, amp, dir):
        pass

    def attack(self):#called from states, attack main
        dir, amp = self.angle_state.get_angle()
        attack = Projectile_1(self.rect.topleft, self.game_objects, dir = dir, amp = amp)#make the object
        self.projectiles.add(attack)#add to group but in main phase

    def update_vel(self, dt):
        pass

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, angle = self.angle_state.angle, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

    def on_attack_timeout(self):
        self.flags['attack_able'] = True

class Sandrew(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/sandrew/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200, 25]
        self.aggro_distance = [250, 25]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack = Hurt_box

class Vildswine(Enemy):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/vildswine/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200, 25]
        self.aggro_distance = [250, 25]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack = Hurt_box

class Rav(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/rav/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)
        self.aggro_distance = [200, 20]#at which distance to the player when you should be aggro -> negative means no
        self.attack_distance = [50, 150]
        self.health = 3
        self.chase_speed = 0.8
        self.patrol_speed = 0.3
        self.patrol_timer = 220
        #self.animation.framerate = 0.2
        self.currentstate = rav_states.Patrol(self)

    def attack(self):#called from states, attack main
        attack = Hurt_box(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/vatt/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)

        self.health = 3
        self.spirit = 3
        self.flags['aggro'] = False

        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = [60, 30]

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__ == 'Vatt':
                enemy.flags['aggro'] = True
                enemy.AI.handle_input('Hurt')

    def patrol(self, direction):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3 * direction[0]

class Maggot(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/maggot/',game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/maggot/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,30)
        self.currentstate = states_maggot.Idle(self)
        self.animation.play('fall_stand')
        self.health = 1

        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.friction[0] = C.friction[0]*2

class Larv_base(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def walk(self):
        self.velocity[0] += self.dir[0]*0.22

class Larv(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/larv/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/enemies/larv/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.attack_distance = [0,0]
        self.currentstate.enter_state('Patrol')

    def loots(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = Larv_jr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Larv_jr(Larv_base):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/larv_jr/', game_objects, True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],22,12)
        self.attack_distance = [0,0]
        self.init_x = self.rect.x
        self.patrol_dist = 100
        self.health = 3

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal

class Larv_poison(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/larv_poison/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.aggro_distance = [180,150]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack_distance = [200,180]

    def attack(self):#called from states, attack main
        attack = Poisonblobb(self.rect.topleft, self.game_objects, dir = self.dir)#make the object
        self.projectiles.add(attack)#add to group but in main phase

class Larv_wall(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/slime_wall/', game_objects, flip_x = True)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)

        self.angle = 0
        self.friction = [0.1, 0.1]
        self.clockwise = 1#1 is clockqise, -1 is counter clockwise
        self.currentstate = larv_wall_states.Floor(self)
        self.dir[0] = -self.clockwise

    def update_vel(self):
        pass

    def knock_back(self,dir):
        pass

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0, shader = self.shader)#shader render

class Shroompoline(Enemy):#an enemy or interactable?
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/shroompolin/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box = pygame.Rect(pos[0],pos[1],32,10)
        self.flags['aggro'] = False#player collision
        self.flags['invincibility'] = True

    def player_collision(self, player):
        if self.game_objects.player.velocity[1] > 0:#going down
            offset = self.game_objects.player.velocity[1] + 1
            if self.game_objects.player.hitbox.bottom < self.jump_box.top + offset:
                self.currentstate.enter_state('Hurt')
                self.game_objects.player.velocity[1] = -10
                player.flags['shroompoline'] = True
                self.game_objects.player.currentstate.enter_state('Jump_main')
                self.game_objects.timer_manager.start_timer(C.shroomjump_timer_player, player.on_shroomjump_timout)#adds a timer to timer_manager and sets self.invincible to false after a while

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

    def chase(self):#called from AI: when chaising
        pass

    def patrol(self,position):#called from AI: when patroling
        pass

class Kusa(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/kusa/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)

        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = [30, 30]
        self.health = 1
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp=2,duration=30)#amplitude and duration

class Svampis(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/svampis/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)

        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = [30, 30]
        self.health = 1
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp=2,duration=30)#amplitude and duration

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('assets/sprites/enteties/enemies/egg/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.number = random.randint(1, 4)
        self.aggro_distance = -1 #if negative, it will not go into aggro

    def knock_back(self,dir):
        pass

    def death(self):
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-100, 100),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Cultist_rogue(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Cultist_rogue.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 40, 40)
        self.health = 3
        self.attack_distance = [80,10]
        self.currentstate = states_rogue_cultist.Idle(self)

    def pool(game_objects):
        Cultist_rogue.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/cultist_rogue/',game_objects)

    def release_texture(self):
        pass

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('cultist_killed')

class Cultist_warrior(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Cultist_warrior.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]

    def pool(game_objects):
        Cultist_warrior.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/cultist_warrior/',game_objects)

    def release_texture(self):
        pass

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('cultist_killed')

class Shadow_enemy(Enemy):#enemies that can onlly take dmg in light -> dark forst
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def check_light(self):
        for light in self.game_objects.lights.lights_sources:
            if not light.shadow_interact: continue
            collision = self.hitbox.colliderect(light.hitbox)
            if collision:
                self.light()
                return
        self.no_light()

    def no_light(self):
        self.flags['invincibility'] = True

    def light(self):
        self.flags['invincibility'] = False

class Shadow_warrior(Shadow_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/cultist_warrior/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]

    def update(self, dt):
        super().update(dt)
        self.check_light()

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

#animals
class Bird(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/animals/bluebird/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_bird.Idle(self)
        self.flags['aggro'] = False
        self.health = 1
        self.aggro_distance = [100,50]#at which distance is should fly away

    def knock_back(self, amp, dir):
        pass

class Reindeer(Boss):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Reindeer.sprites
        self.image = self.sprites['idle_nice'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 35, 45)
        self.health = 2
        self.currentstate = task_manager.TaskManager(self, reindeer_states.STATE_REGISTRY, reindeer_states.PATTERNS)

        self.ability = 'dash_ground_main'#the stae of image that will be blitted to show which ability that was gained
        self.attack_distance = [100, 50]
        #self.chase_distance = [200, 50]
        self.jump_distance = [240, 50]
        self.attack = Hurt_box

        self.light = self.game_objects.lights.add_light(self, radius = 150)
        self.animation.framerate = 1/6

    def pool(game_objects):
        Reindeer.sprites = read_files.load_sprites_dict('assets/sprites/enteties/boss/reindeer/',game_objects)

    def release_texture(self):
        pass

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.currentstate.unlock_state('dash')#append dash abillity to available states

    def slam_attack(self):#called from states, attack main
        self.game_objects.cosmetics.add(ChainProjectile(self.rect.center, self.game_objects, SlamAttack, direction = self.dir, distance = 50, number = 5, frequency = 20))

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.world_state.cutscene_complete('boss_deer_encounter')#so not to trigger the cutscene again

    def kill(self):
        super().kill()
        self.game_objects.lights.remove_light(self.light)#should be removed when reindeer is removed from the game

class Butterfly(FlyingEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/boss/butterfly/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos,self.image.size)
        self.hitbox = self.rect.copy()
        self.currentstate = states_butterfly.Idle(self)
        self.health =20

    def knock_back(self,dir):
        pass

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('butterfly_killed')

    def right_collision(self,block, type = 'Wall'):
        pass

    def left_collision(self,block, type = 'Wall'):
        pass

    def down_collision(self,block):
        pass

    def top_collision(self,block):
        pass

class Rhoutta_encounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('assets/sprites/enteties/boss/rhoutta/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 3
        self.attack_distance = [100,10]
        self.attack = Sword
        self.dmg = 0

    def dead(self):
        self.game_objects.game.state_manager.exit_state()
        self.game_objects.player.reset_movement()
        self.game_objects.game.state_manager.enter_state(state_name = 'Defeated_boss', category = cutscenes, page = 'Rhoutta_encounter')