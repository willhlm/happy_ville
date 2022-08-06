import pygame
import states

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def pass_through(self):
        ramp = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.platforms_ramps,Collisions.collided)
        if ramp:
            self.game_objects.player.velocity[1] = 0
            self.game_objects.player.go_through = True

    def interact_cosmetics(self):#bushes
        for cosmetic in self.game_objects.interacting_cosmetics.sprites():

            collision_entity = pygame.sprite.spritecollideany(cosmetic,self.game_objects.players,Collisions.collided)
            if collision_entity:
                cosmetic.collide()
            else:
                cosmetic.interacted=False

            collision_fprojectile = pygame.sprite.spritecollideany(cosmetic,self.game_objects.fprojectiles,Collisions.collided)
            if collision_fprojectile:
                cosmetic.cut()

    def thunder_attack(self,aura):
        return pygame.sprite.spritecollide(aura,self.game_objects.enemies,False,Collisions.collided)#check collision

    @staticmethod
    def counter(fprojectiles,eprojectiles):
        for projectile in fprojectiles.sprites():#go through the group
            collision_epro = pygame.sprite.spritecollideany(projectile,eprojectiles,Collisions.collided)
            if collision_epro:
                projectile.collision_projectile(collision_epro)

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
                if str(type(collision_enemy.currentstate).__name__) is not 'Hurt':#change to some invinsibillity thingy maybe
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
            if str(type(collision_enemy.currentstate).__name__) is not 'Death':
                collision_enemy.player_collision()

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
            npc.interact()

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
                if trigger.event_type=='cutscene':
                    if trigger.event not in self.game_objects.cutscenes_complete:#if the cutscene has not been shown before. Shold we kill the object instead?    
                        new_game_state = states.Cutscenes(self.game_objects.game,trigger.event)
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

            static_entity_y = pygame.sprite.spritecollideany(entity,static_entities,Collisions.collided)
            if static_entity_y:
                static_entity_y.collide_y(entity)

            ramp = pygame.sprite.spritecollideany(entity,ramps,Collisions.collided)
            if ramp:
                ramp.collide(entity)
            else:
                entity.go_through = False

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_entities):
        return dynamic_Entities.hitbox.colliderect(static_entities.hitbox)
