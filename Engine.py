import pygame

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def pass_through(self):#for ramps
        ramp = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.platforms_ramps,Collisions.collided)
        if ramp:
            self.game_objects.player.velocity[1] = 0
            self.game_objects.player.go_through = True

    def cosmetics_collision(self):#bushes, check plater
        for cosmetic in self.game_objects.interacting_cosmetics.sprites():
            collision_entity = pygame.sprite.spritecollideany(cosmetic,self.game_objects.players,Collisions.collided)
            if collision_entity:
                cosmetic.player_collision()
            else:
                cosmetic.interacted = False

    def thunder_attack(self,aura):
        return pygame.sprite.spritecollide(aura,self.game_objects.enemies,False,Collisions.collided)#check collision

    @staticmethod
    def counter(fprojectiles,eprojectiles):
        for projectile in fprojectiles.sprites():#go through the group
            collision_epro = pygame.sprite.spritecollideany(projectile,eprojectiles,Collisions.collided)
            if collision_epro:
                projectile.collision_projectile(collision_epro)

    def projectile_collision(self,projectiles,enemies):
        for projectile in projectiles.sprites():#go through the group

            #projectile collision?
            collision_plat = pygame.sprite.spritecollideany(projectile,self.game_objects.platforms,Collisions.collided)
            collision_enemy = pygame.sprite.spritecollideany(projectile,enemies,Collisions.collided)
            collision_inetractables = pygame.sprite.spritecollideany(projectile,self.game_objects.interacting_cosmetics,Collisions.collided)

            #if hit chest, bushes
            if collision_inetractables:
                projectile.collision_inetractables(collision_inetractables)

            #if hit enemy
            if collision_enemy:
                if str(type(collision_enemy.currentstate).__name__) is not 'Hurt':#change to some invinsibillity thingy maybe
                    projectile.collision_enemy(collision_enemy)

            #hit platform
            elif collision_plat:
                projectile.collision_plat()

    #take damage if collide with enemy
    def player_collision(self,enteties):
        collision_enteties=pygame.sprite.spritecollideany(self.game_objects.player,enteties,Collisions.collided)#check collision
        if collision_enteties:
            collision_enteties.player_collision()

    #npc player conversation, when pressing t
    def check_interaction_collision(self):
        npc =  pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.npcs,Collisions.collided)#check collision
        interactable = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.interactables,Collisions.collided)#check collision

        if npc:
            npc.interact()
        elif interactable:
            interactable.interact()

    #collision of player and enemy: setting the flags depedning on the collisoin directions
    #collisions between entities-groups: a dynamic and a static one

    def platform_collision(self,dynamic_Entities):
        for entity in dynamic_Entities.sprites():
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}

            #move in x every dynamic sprite
            entity.rect.center = [round(entity.rect.center[0] + entity.velocity[0]), entity.rect.center[1]]
            entity.update_hitbox()

            static_entity_x = pygame.sprite.spritecollideany(entity,self.game_objects.platforms,Collisions.collided)
            if static_entity_x:
                static_entity_x.collide_x(entity)

            #move in y every dynamic sprite
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.velocity[1])]
            entity.update_hitbox()#follow with hitbox

            static_entity_y = pygame.sprite.spritecollideany(entity,self.game_objects.platforms,Collisions.collided)
            if static_entity_y:
                static_entity_y.collide_y(entity)

            ramp = pygame.sprite.spritecollideany(entity,self.game_objects.platforms_ramps,Collisions.collided)
            if ramp:
                ramp.collide(entity)
            else:
                entity.go_through = False

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_entities):
        return dynamic_Entities.hitbox.colliderect(static_entities.hitbox)
