import pygame, random, sys, math
import read_files, dialogue
import constants as C

from entities_core import Staticentity, Animatedentity, Platform_entity, Character

from states import states_enemy, states_enemy_flying, states_NPC
from ai import AI_enemy, AI_enemy_flying

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class Enemy(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal
        self.original_pos = pos

        self.currentstate = states_enemy.Idle(self)
        self.AI = AI_enemy.AI(self)

        self.inventory = {'Amber_droplet':random.randint(5,10),'Bone':1,'Heal_item':1}#thigs to drop wgen killed
        self.spirit = 10
        self.health = 3

        self.flags = {'aggro': True, 'invincibility': False, 'attack_able': True}#'attack able': a flag used as a cooldown of attack
        self.dmg = 1#projectile damage

        self.attack_distance = [0,0]#at which distance to the player to attack
        self.aggro_distance = [100,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.chase_speed = 0.6

    def update(self):
        self.AI.update()#tell what the entity should do -> shuold be first in upate loop
        self.hitstop_states.update()#need to be after update_vel and animation, and AI
        self.group_distance()

    def player_collision(self, player):#when player collides with enemy
        if type(player.currentstate).__name__ in ['Thunder_main', 'Thunder_post']:
            self.take_dmg(1)
            pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])
            self.knock_back([pm_one,0])
        else:
            if not self.flags['aggro']: return
            if player.flags['invincibility']: return
            player.take_dmg(1)
            pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])
            player.knock_back([pm_one,0])

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
        self.kill()

    def loots(self):#called when dead
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop,self.game_objects)#make a class based on the name of the key
                self.game_objects.loot.add(obj)
            self.inventory[key] = 0

    def countered(self):#purple infifite stone
        self.velocity[0] = -30*self.dir[0]
        self.currentstate = states_enemy.Stun(self,duration=30)#should it overwrite?

    def health_bar(self):#called from omamori Boss_HP
        pass

    def chase(self, position = [0,0]):#called from AI: when chaising
        self.velocity[0] += self.dir[0] * self.chase_speed

    def patrol(self, position = [0,0]):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3

class Flying_enemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8,C.friction[0]*0.8]

        self.max_vel = [C.max_vel[0],C.max_vel[0]]
        self.dir[1] = 1
        self.AI = AI_enemy_flying.Patrol(self)
        self.currentstate = states_enemy_flying.Idle(self)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def knock_back(self,dir):
        amp = [20,20]
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]

    def chase(self, target_distance):#called from AI: when chaising
        self.velocity[0] += (target_distance[0])*0.002 + self.dir[0]*0.1
        self.velocity[1] += (target_distance[1])*0.002 + sign(target_distance[1])*0.1

    def patrol(self, position):#called from AI: when patroling
        self.velocity[0] += 0.005*(position[0]-self.rect.centerx)
        self.velocity[1] += 0.005*(position[1]-self.rect.centery)

    def walk(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.3)
        self.velocity[1] += amp*math.sin(5*time)# - self.entity.dir[1]*0.1

    def update_rect_y(self):
        self.rect.center = self.hitbox.center
        self.true_pos[1] = self.rect.top

    def update_rect_x(self):
        self.rect.center = self.hitbox.center
        self.true_pos[0] = self.rect.left

    def killed(self):#called when death animation starts playing
        pass

    def limit_y(self):
        pass

class NPC(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.name = str(type(self).__name__)#the name of the class
        self.load_sprites()
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox

        self.currentstate = states_NPC.Idle(self)
        self.dialogue = dialogue.Dialogue(self)#handles dialoage and what to say
        self.define_conversations()

    def define_conversations(self):#should depend on NPC
        self.priority = ['reindeer','ape']#priority events to say
        self.event = ['aslat']#normal events to say
        self.quest = []

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict("Sprites/Enteties/NPC/" + self.name + "/animation/", self.game_objects)
        img = pygame.image.load('Sprites/enteties/NPC/' + self.name +'/potrait.png').convert_alpha()
        self.portrait = self.game_objects.game.display.surface_to_texture(img)#need to save in memoery

    def update(self):
        super().update()
        #self.group_distance()

    def render_potrait(self, terget):
        self.game_objects.game.display.render(self.portrait, terget, position = (32,32))#shader render

    def interact(self):#when plater press t
        self.game_objects.game.state_manager.enter_state('Conversation', npc = self)

    def random_conversation(self, text):#can say stuff through a text bubble
        random_conv = dialogue.Conversation_bubbles(self.rect.topright,self.game_objects, text)
        self.game_objects.cosmetics.add(random_conv)

    def buisness(self):#enters after conversation
        pass

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10
        self.health_bar = Health_bar(self)

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.update_event(str(type(self).__name__).lower())

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites[self.ability][0], text = self.ability)
        self.game_objects.game.state_manager.enter_state(state_name = 'Defeated_boss', category = 'game_states_cutscenes')

    def health_bar(self):#called from omamori Boss_HP
        self.health_bar.max_health = self.health
        self.game_objects.cosmetics.add(self.health_bar)

    def give_abillity(self):
        self.game_objects.player.abilities.spirit_abilities[self.ability] = getattr(sys.modules[__name__], self.ability)(self.game_objects.player)

    def knock_back(self,dir):
        pass

class Projectiles(Platform_entity):#projectiels
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.lifetime = kwarg.get('lifetime', 300)
        self.flags = {'invincibility': False, 'charge_blocks': kwarg.get('charge_blocks', False)}#if they can break special blocks

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    #collisions
    def collision_platform(self, collision_plat):#collision platform
        collision_plat.take_dmg(self)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        collision_enemy.take_dmg(self.dmg)

    def collision_interactables(self,interactable):#collusion interactables
        interactable.take_dmg(self)#some will call clash_particles but other will not. So sending self to interactables

    def reflect(self, dir, pos, clamp_value = 10):#projectile collision when purple infinity stone is equipped: pos, dir are aila sword
        dy = max(-clamp_value, min(clamp_value, self.rect.centery - pos[1]))
        dx = max(-clamp_value, min(clamp_value, self.rect.centerx - pos[0]))

        if dir[1] != 0:#up or down
            self.velocity[0] = dx * 0.2
            self.velocity[1] = -10 * dir[1]
        else:#right or left
            self.velocity[0] = 10 * dir[0]
            self.velocity[1] = dy * 0.2

    def take_dmg(self, dmg):
        pass

    #pltform, ramp collisions.
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        pass

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        pass

    def right_collision(self, block, type = 'Wall'):
        self.collision_platform(block)

    def left_collision(self, block, type = 'Wall'):
        self.collision_platform(block)

    def down_collision(self, block):
        self.collision_platform(block)

    def top_collision(self, block):
        self.collision_platform(block)

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps: it makes a smooth drop
        pass

    def release_texture(self):#i guess all projectiles will have a pool
        pass

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

class Melee(Projectiles):
    def __init__(self, entity, **kwarg):
        super().__init__([0,0], entity.game_objects, **kwarg)
        self.entity = entity#needs entity for making the hitbox follow the player in update hitbox
        self.dir = kwarg.get('dir', entity.dir.copy())
        self.direction_mapping = {(0, 0): ('center', 'center'), (1, 1): ('midbottom', 'midtop'),(-1, 1): ('midbottom', 'midtop'), (1, -1): ('midtop', 'midbottom'),(-1, -1): ('midtop', 'midbottom'),(1, 0): ('midleft', 'midright'),(-1, 0): ('midright', 'midleft')}

    def update_hitbox(self):#called from update hirbox in plaform entity
        rounded_dir = (sign(self.dir[0]), sign(self.dir[1]))#analogue controls may have none integer values
        hitbox_attr, entity_attr = self.direction_mapping[rounded_dir]
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes

    def reflect(self, dir, pos):#called from sword collision_projectile, purple initinty stone
        return
        self.entity.countered()
        self.kill()

    def update_rect_y(self):
        pass

    def update_rect_x(self):
        pass

class Loot(Platform_entity):#
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.description = ''
        self.bounce_coefficient = 0.6

    def update_vel(self):#add gravity
        self.velocity[1] += 0.3*self.game_objects.game.dt

    def update(self):
        super().update()
        self.update_vel()

    def attract(self, pos):#the omamori calls on this in loot group
        pass

    def interact(self, player):#when player press T
        pass

    def player_collision(self, player):#when the player collides with this object
        pass

    def release_texture(self):#stuff that have pool shuold call this
        pass

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')
        self.velocity[0] = 0.5 * self.velocity[0]
        self.velocity[1] = -self.bounce_coefficient*self.velocity[1]
        self.bounce_coefficient *= self.bounce_coefficient

    #plotfprm collisions
    def top_collision(self,block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self,block):
        super().down_collision(block)
        self.velocity[0] = 0.5 * self.velocity[0]
        self.velocity[1] = -self.bounce_coefficient*self.velocity[1]
        self.bounce_coefficient *= self.bounce_coefficient

    def right_collision(self,block, type = 'Wall'):
        super().right_collision(block, type)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,block, type = 'Wall'):
        super().left_collision(block, type)
        self.velocity[0] = -self.velocity[0]

    def limit_y(self):
        if self.bounce_coefficient < 0.1:#to avoid falling through one way collisiosn
            self.velocity[1] = max(self.velocity[1],0.6)                        

class Enemy_drop(Loot):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.lifetime = 500
        self.velocity = [random.uniform(-3, 3),-3]

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt
        self.destory()

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity = [0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self, player):#when the player collides with this object
        if self.currentstate.__class__.__name__ == 'Death': return#enter only once
        self.game_objects.sound.play_sfx(self.sounds['death'][0])#should be in states
        name = self.__class__.__name__.lower()
        player.backpack.inventory.add(name)
        self.currentstate.handle_input('Death')

class Interactable(Animatedentity):#interactables
    def __init__(self, pos, game_objects, sfx = None):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft
        if sfx: self.sfx = pygame.mixer.Sound('audio/SFX/environment/' + sfx + '.mp3')
        else: self.sfx = None # make more dynamic incase we want to use more than just mp3

    def update(self):
        super().update()
        self.group_distance()

    def play_sfx(self):
        self.game_objects.sound.play_sfx(self.sfx)

    def interact(self):#when player press T
        pass

    def player_collision(self, player):#player collision
        pass

    def player_noncollision(self):#when player doesn't collide: for grass
        pass

    def take_dmg(self, projectile):#when player hits with e.g. sword
        pass

