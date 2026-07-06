import random
from gameplay.entities.base.character import Character
from engine.utils.functions import sign
from gameplay.entities.shared.components.hit import hit_effects
from gameplay.entities.shared.components.loot.item_loot_emitter import ItemLootEmitterComponent
from gameplay.entities.enemies.common.shared.effects.death_effects import EnemyDeathEffects
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.enemies.configs.base_enemy_config import ENEMY_CONFIG

class Enemy(Character):
    kill_signal = None

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)      
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal
        self.original_pos = pos

        self.config = ENEMY_CONFIG['base']
        self.currentstate = StateManager(self)

        self.inventory = {'amber_droplet':random.randint(1,3)}#thigs to drop wgen killed
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)

        self.flags = {'aggro': True, 'attack_able': True, 'hurt_able': True}#'attack able': a flag used as a cooldown of attack
        self.dmg = 1
        self.death_effects = EnemyDeathEffects(self)
        self.loot_emitter = ItemLootEmitterComponent(self, spawn_velocity=[0, -3], spawn_velocity_range=[3, 0])
        
    def update_render(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.shader_state.update_render(scaled_dt)#need to be after animation

    def update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)

        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)

        self.update_vel(scaled_dt)

    def post_physics_update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.consume_contact_state()
        self.currentstate.update(scaled_dt)
        self.animation.update(scaled_dt)

    def player_collision(self, player):#when player collides with enemy
        if not self.flags['aggro']: return
        pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])

        effect = hit_effects.create_contact_effect(
            self.game_objects,
            damage=1,
            knockback=[20, 0],
            hitstop=5,
            attacker=self,
            attacker_dir=[pm_one, 0],
        )
        damage_applied, modified = player.take_hit(effect)# Player takes hit

    def get_state_machine_target(self):
        return self.game_objects.player

    def killed(self):#called at killing blow
        if not self.death_effects.begin_cleanup(): return        
        self.flags['aggro'] = False
                
        self.death_effects.play_kill_sound()
        self.death_effects.emit_particles()
        self.game_objects.world_state.statistics_state.update_kill_statistics(type(self).__name__.lower())
        self._emit_loot()
        self._emit_kill_signal()

    def dead(self):#called when death animation is finished                        
        self.death_effects.play_dead_sound()
        self.death_effects.start_visual()

    def _emit_loot(self):
        self.loot_emitter.emit_inventory(self.inventory)

    def _emit_kill_signal(self):
        if self.kill_signal:
            self.game_objects.signals.emit(self.kill_signal)
