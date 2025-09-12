import pygame

from engine.utils import read_files

from gameplay.entities.items.base.item import Item
from gameplay.entities.items.base.enemy_drop import EnemyDrop
from gameplay.entities.items.base.interactable_item import InteractableItem

#things player can pickup
class Heart_container(Item):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/heart_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update_vel(self, dt):
        self.velocity[1] = 3*dt

    def player_collision(self, player):
        player.max_health += 1
        #a cutscene?
        self.kill()

class Spirit_container(Item):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/spirit_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'A spirit container'

    def update_vel(self, dt):
        self.velocity[1]=3*dt

    def player_collision(self,player):
        player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Item):#genkidama
    def __init__(self, pos, game_objects, ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/soul_essence/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self, player):
        player.backpack.inventory.add(self)
        self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'][self.ID_key] = True#write in the state file that this has been picked up
        #make a cutscene?TODO
        self.kill()

    def update(self, dt):
        super().update(dt)
        obj1 = getattr(particles, 'Spark')(self.rect.center, self.game_objects, distance = 100, lifetime=20, vel={'linear':[2,4]}, fade_scale = 10)
        self.game_objects.cosmetics.add(obj1)

    def update_vel(self):
        pass

class Spiritorb(Item):#the thing that gives spirit
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/spiritorbs/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):
        player.add_spirit(1)
        self.kill()

    def update_vel(self):
        pass

class Amber_droplet(EnemyDrop):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Amber_droplet.sprites
        self.sounds = Amber_droplet.sounds

        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'moneyy'

    def player_collision(self,player):#when the player collides with this object
        super().player_collision(player)
        self.game_objects.world_state.update_statistcis('amber_droplet')
        tot_amber = player.backpack.inventory.get_quantity(self)
        self.game_objects.ui.hud.update_money(tot_amber)

    def pool(game_objects):#all things that should be saved in object pool
        Amber_droplet.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/amber_droplet/',game_objects)
        Amber_droplet.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/items/amber_droplet/')

    def set_ui(self):#called from backpask
        self.animation.play('ui')

class Bone(EnemyDrop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Bone.sprites
        self.sounds = Bone.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self):
        if self.game_objects.player.backpack.inventory.get_quantity('bone') <= 0: return#if we don't have bones
        self.game_objects.player.backpack.inventory.remove('bone')
        self.game_objects.player.backpack.map.save_bone(map = self.game_objects.map.level_name, point = self.game_objects.camera_manager.camera.scroll)
        self.game_objects.player.currentstate.enter_state('Plant_bone_main')

    def pool(game_objects):#all things that should be saved in object pool
        Bone.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/bone/',game_objects)
        Bone.sounds = read_files.load_sounds_dict('assets/audio/sfx/audio/sfx/enteties/items/bone/')

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Heal_item(EnemyDrop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Heal_item.sprites
        self.sounds = Heal_item.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Use it to heal'

    def use_item(self):
        if self.game_objects.player.backpack.inventory.get_quantity('heal_item') < 0: return
        self.game_objects.player.backpack.inventory.remove('heal_item')
        self.game_objects.player.heal(1)

    def pool(game_objects):#all things that should be saved in object pool: #obj = cls.__new__(cls)#creatate without runing initmethod
        Heal_item.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/heal_item/',game_objects)
        Heal_item.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/items/heal_item/')

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Tungsten(InteractableItem):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Tungsten.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'A heavy rock'

    def pickup(self, player):
        super().pickup(player)
        player.backpack.inventory.add(self)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/tungsten/',game_objects)
        super().pool(game_objects)

class Rings(InteractableItem):#ring in which to attach radnas
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Rings.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.level = 1
        self.description = 'A ring'
        self.radna = None

    def set_finger(self, finger):
        self.finger = finger
        self.animation.play(self.finger + '_' + str(self.level))

    def update_equipped(self):#caleld from neckalce
        self.radna.equipped()

    def handle_press_input(input):#called from neckalce
        self.radna.handle_press_input(input)

    def upgrade(self):
        self.level += 1
        self.animation.play(self.finger + '_' + str(self.level))

    def pickup(self, player):
        super().pickup(player)
        player.backpack.radna.add_ring(self)
        self.set_owner(player)

    def attach_radna(self, radna):
        self.radna = radna
        self.radna.set_owner(self.entity)
        self.radna.attach()

    def detach_radna(self, radna):
        self.radna.detach()
        self.radna.set_owner(None)
        self.radna = None

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/rings/',game_objects)
        super().pool(game_objects)

class Radna(InteractableItem):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.description = ''#for inventory
        self.level = 1#the level of ring reuried to equip
        self.entity = None#defualt is no owner

    def equipped(self):#called from the rings, when rings are updated
        pass

    def handle_press_input(input):#called from neckalce
        pass

    def pickup(self, player):
        super().pickup(player)
        copy_item = type(self)([0,0], self.game_objects)
        player.backpack.radna.add(copy_item)
        self.game_objects.signals.emit('item_interacted', item = self, player = player)

    def detach(self):#called when de-taching the radna to ring
        self.shader = None#for ui

    def attach(self):#called when attaching the radna to ring
        self.shader = self.game_objects.shaders['colour'] #for ui

class Half_dmg(Radna):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Half_dmg.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level = 1
        self.description = 'Take half dmg ' + '[' + str(self.level) + ']'

    def attach(self):
        super().attach()
        self.entity.damage_manager.add_modifier('Half_dmg')

    def detach(self):
        super().detach()
        self.entity.damage_manager.remove_modifier('Half_dmg')

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/half_dmg/',game_objects)#for inventory
        super().pool(game_objects)

class Loot_magnet(Radna):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Loot_magnet.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'Attracts loot ' + '[' + str(self.level) + ']'

    def equipped(self):#an update that should be called when equppied
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/loot_magnet/',game_objects)#for inventory
        super().pool(game_objects)

class Boss_HP(Radna):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Boss_HP.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level = 2
        self.description = 'Visible boss HP ' + '[' + str(self.level) + ']'

    def attach(self):
        for enemy in self.entity.game_objects.enemies.sprites():
            enemy.health_bar()#attached a healthbar on boss

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/boss_HP/',game_objects)#for inventor
        super().pool(game_objects)

class Indincibillity(Radna):#extends the invincibillity time
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Runspeed(Radna):#increase the runs speed
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Dashpeed(Radna):#decrease the dash cooldown?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Shields(Radna):#autoamtic shield that negates one damage, if have been outside combat for a while?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Wallglue(Radna):#to make aila stick to wall, insead of gliding?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Hover(Radna):#If holding jump button, make a small hover
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Infinity_stones(InteractableItem):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sword = kwarg.get('entity', None)
        self.description = ''

    def set_pos(self, pos):#for inventory
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self, player):#called from sword when balcksmith attached the stone
        pass

    def pickup(self, player):
        super().pickup(player)
        self.attach(player)
        self.sword = player.sword

class Red_infinity_stone(Infinity_stones):#more dmg
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Red_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'red':[255,64,64,255]}
        self.description = '10 procent more damage'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/red/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self):
        self.sword.dmg *= 1.1

class Green_infinity_stone(Infinity_stones):#faster slash (changing framerate)
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Green_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'green':[105,139,105,255]}
        self.description = 'fast sword swings'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/green/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['slash'].enter_state('Slash', 'slash')

class Blue_infinity_stone(Infinity_stones):#get spirit at collision
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Blue_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'blue':[0,0,205,255]}
        self.description = 'add spirit to the swinger'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/blue/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['enemy_collision'].enter_state('Enemy_collision', 'enemy_collision')

class Orange_infinity_stone(Infinity_stones):#bigger hitbox
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Orange_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'orange':[255,127,36,255]}
        self.description = 'larger hitbox'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/orange/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y, 80, 40)
        self.sword.hitbox = self.sword.rect.copy()

class Purple_infinity_stone(Infinity_stones):#reflect projectile -> crystal caves
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Purple_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'purple':[154,50,205,255]}
        self.description = 'reflects projectiels'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/purple/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['projectile_collision'].enter_state('Projectile_collision', 'projectile_collision')