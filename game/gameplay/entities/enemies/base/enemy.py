import random
from gameplay.entities.base.character import Character
from gameplay.entities.enemies.ground import states_enemy

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

        self.inventory = {'amber_droplet':random.randint(1,3)}#thigs to drop wgen killed
        self.spirit = 10
        self.health = 3

        self.flags = {'aggro': True, 'invincibility': False, 'attack_able': True, 'hurt_able': False}#'attack able': a flag used as a cooldown of attack
        self.dmg = 1#projectile damage

        self.attack_distance = [0,0]#at which distance to the player to attack
        self.aggro_distance = [100,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.chase_speed = 0.6

    def update_render(self, dt):
        self.hitstop_states.update_render(dt)

    def update(self, dt):
        self.hitstop_states.update(dt)
        self.group_distance()

    def player_collision(self, player):#when player collides with enemy
        if type(player.currentstate).__name__ in ['Thunder_main', 'Thunder_post']:
            pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])            
            self.take_dmg(dmg = 1, effects = [lambda: self.knock_back(amp = [50, 0], dir = [pm_one, 0])])
        else:
            if not self.flags['aggro']: return
            if player.flags['invincibility']: return
            pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])
            player.take_dmg(dmg = 1, effects = [lambda: player.knock_back(amp = [50, 0], dir = [pm_one, 0])])#player take damage

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

    def modify_hit(self, effect):
        return effect