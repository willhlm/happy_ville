import pygame
import states

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    @staticmethod
    def counter(fprojectiles,eprojectiles):
        for projectile in fprojectiles.sprites():#go through the group
            if type(projectile).__name__ == 'Shield':
                collision_epro = pygame.sprite.spritecollideany(projectile,eprojectiles,Collisions.collided)
                if collision_epro:
                    collision_epro.countered(projectile)
                    projectile.kill()#kill the shoeld

    @staticmethod
    def weather_paricles(weathers,platforms):
        for particle in weathers.sprites():#go through the group
            collision = pygame.sprite.spritecollideany(particle,platforms)
            if collision:
                particle.collision()

    @staticmethod
    def action_collision(projectiles,platforms,enemies):
        for projectile in projectiles.sprites():#go through the group

            #projectile collision?
            collision_plat = pygame.sprite.spritecollideany(projectile,platforms,Collisions.collided)
            collision_enemy = pygame.sprite.spritecollideany(projectile,enemies,Collisions.collided)

            #if hit enemy
            if collision_enemy:
                if str(type(collision_enemy.currentstate).__name__) is not 'Hurt':
                    collision_enemy.take_dmg(projectile.dmg)
                    projectile.collision_enemy(collision_enemy)
            #hit platform
            elif collision_plat:
                projectile.collision_plat()

    #take damage if collide with enemy
    @staticmethod
    def check_enemy_collision(player,enemies):
        collision_enemy=pygame.sprite.spritecollideany(player,enemies,Collisions.collided)#check collision

        if collision_enemy:
            if str(type(collision_enemy.currentstate).__name__) is not 'Death' and collision_enemy.aggro:

                player.take_dmg(10)
                sign=(player.hitbox.center[0]-collision_enemy.hitbox.center[0])
                if sign>0:
                    player.velocity[0]=10#knock back of player
                else:
                    player.velocity[0]=-10#knock back of player

    #pickup loot
    @staticmethod
    def pickup_loot(player,loots):
        collision_loot=pygame.sprite.spritecollideany(player,loots,Collisions.collided)#check collision
        if collision_loot:
            collision_loot.pickup(player)

    #npc player conversation
    def check_interaction_collision(self):
        self.check_npc_collision()
        self.check_interactables()

    def check_npc_collision(self):
        npc =  pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.npcs,Collisions.collided)#check collision
        if npc:
            new_state = states.Conversation(self.game_objects.game, npc)
            new_state.enter_state()

    #interact with chests
    def check_interactables(self):
        collision = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.interactables,Collisions.collided)#check collision
        if collision:
            collision.interact(self.game_objects.player)

    def check_trigger(self,player,triggers):
        trigger = pygame.sprite.spritecollideany(player,triggers,Collisions.collided)

        if trigger:
            if type(trigger).__name__ == 'Path_col':
                self.game_objects.sound.pause_bg_sound()
                self.game_objects.player.enter_idle()
                self.game_objects.player.reset_movement()
                self.game_objects.load_map(trigger.destination, trigger.spawn)

            elif type(trigger).__name__ == 'Trigger':
                if trigger.event not in self.game_objects.cutscenes_complete:#if the cutscene has not been shown before
                    if trigger.event_type=='cutscene_file':
                        new_game_state = states.Cutscene_file(self.game_objects.game,trigger.event)
                        new_game_state.enter_state()
                    elif trigger.event_type=='cutscene_engine':
                        new_game_state = states.Cutscene_engine(self.game_objects.game,trigger.event)
                        new_game_state.enter_state()

    #collision of player and enemy: setting the flags depedning on the collisoin directions
    #collisions between entities-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_Entities,static_entities,ramps):

        for entity in dynamic_Entities.sprites():
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}

            #move in x every dynamic sprite
            entity.rect.center = [round(entity.rect.center[0] + entity.velocity[0]), entity.rect.center[1]]
            entity.update_hitbox()

            static_entity_x = pygame.sprite.spritecollideany(entity,static_entities,Collisions.collided)
            if static_entity_x:
                static_entity_x.collide_x(entity)

            #move in y every dynamic sprite
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.velocity[1])]
            entity.update_hitbox()#follow with hitbox

            ramp = pygame.sprite.spritecollideany(entity,ramps,Collisions.collided)
            ramp_collision = False

            if ramp:
                ramp_offset = 1 #make transitions smoother, maybe implement this differently
                x_tot = ramp.size[0]
                y_tot = ramp.size[1]
                x_1 = entity.hitbox.centerx - ramp.hitbox.left
                if  (0 < x_1 < x_tot) and entity.velocity[1] > 0:
                    if ramp.orientation == 0:
                        y = (x_tot - x_1 + 2)*(y_tot/x_tot)
                        y = int(ramp.hitbox.bottom - y - ramp_offset)

                        if entity.hitbox.bottom <= y:
                            pass
                        else:
                            ramp_collision = True
                            entity.hitbox.bottom = max(y, ramp.hitbox.top)
                            entity.collision_types['bottom'] = True

                    elif ramp.orientation == 1:
                        y = (x_1+4)*(y_tot/x_tot)
                        y = int(ramp.hitbox.bottom - y)

                        if entity.hitbox.bottom <= y:
                            pass
                        else:
                            ramp_collision = True
                            entity.hitbox.bottom = max(y, ramp.hitbox.top)
                            entity.collision_types['bottom'] = True
                    entity.update_rect()

            if not ramp_collision:
                static_entity_y = pygame.sprite.spritecollideany(entity,static_entities,Collisions.collided)
                if static_entity_y:
                    static_entity_y.collide_y(entity)

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_entities):
        return dynamic_Entities.hitbox.colliderect(static_entities.hitbox)
