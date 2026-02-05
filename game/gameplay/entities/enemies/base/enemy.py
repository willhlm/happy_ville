import random
from gameplay.entities.base.character import Character
from engine.utils.functions import sign
from gameplay.entities.shared.components import hit_effects
from gameplay.entities.enemies.common.shared.states.state_manager import StateManager
from config.enemy import ENEMY_CONFIG 

class Enemy(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)      
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal
        self.original_pos = pos

        self.config = ENEMY_CONFIG['passive']
        self.currentstate = StateManager(self)

        self.inventory = {'amber_droplet':random.randint(1,3)}#thigs to drop wgen killed
        self.health = self.config['health']    

        self.flags = {'aggro': True, 'invincibility': False, 'attack_able': True, 'hurt_able': True}#'attack able': a flag used as a cooldown of attack
        self.dmg = 1
        
        self.contact_effect = hit_effects.create_contact_effect(damage = 1, knockback = [20, 0], hitstop = 5, attacker = self)#collision with player

    def update_render(self, dt):
        self.shader_state.update_render(dt)#need to be after animation

    def update(self, dt):
        self.hitstop.update(dt)
        scaled_dt = self.get_sim_dt(dt)

        self.update_vel(scaled_dt)
        self.currentstate.update(scaled_dt)#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update(scaled_dt)#need to be after currentstate since animation will animate the current state

        self.group_distance()

    def player_collision(self, player):#when player collides with enemy
        if not self.flags['aggro']: return
        pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])
        
        effect = self.contact_effect.copy()
        effect.meta['attacker_dir'] = [pm_one, 0]  # Push player away                   
        damage_applied, modified = player.take_hit(effect)# Player takes hit

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
        self.kill()

    def loots(self):#called when dead
        for key in self.inventory.keys():#go through all loot
            for i in range(0, self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = self.game_objects.registry.fetch('items', key)(self.hitbox.midtop, self.game_objects) 
                obj.spawn_position()                                         
                self.game_objects.loot.add(obj)
            self.inventory[key] = 0

    def health_bar(self):#called from omamori Boss_HP
        pass

    def chase(self, position = [0,0]):#called from AI: when chaising
        self.velocity[0] += self.dir[0] * self.chase_speed

    def patrol(self, position = [0,0]):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3      