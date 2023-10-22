import pygame, math

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def check_ground(self,point):#called from AI
        for platform in self.game_objects.platforms:
            if platform.hitbox.collidepoint(point):
                return True
        return False

    def check_ramp(self,point):#called from limit_y in platform entities
        for platform in self.game_objects.platforms_ramps:
            if platform.hitbox.collidepoint(point):
                if platform.target > point[1]: return False#if the ramp target position is far way from the check point, then it is most likely just the hitbox
                return True
        return False

    def pass_through(self, entity):#called when pressing down
        self.game_objects.player.hitbox.bottom += 1
        #pos = entity.hitbox.midbottom
        ramp = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.platforms_ramps,Collisions.collided)
        platform = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.platforms,Collisions.collided)

        if platform:
            if ramp:#if on ramp hitbox and pltoform
                self.game_objects.player.velocity[1] = 1#so that it looks more natural (cannot be 0, needs to be finite)
            self.game_objects.player.go_through = platform.go_through#a flag that determines if one can go through

        if ramp:
            if ramp.target > self.game_objects.player.hitbox.bottom: return#if from above, do nothing
            elif not self.game_objects.player.go_through:#enter only once
                self.game_objects.player.velocity[1] = 1#so that it looks more natural (cannot be 0, needs to be finite)
            self.game_objects.player.go_through = ramp.go_through#a flag that determines if one can go through


    def interactables_collision(self):#interactables
        for interactable in self.game_objects.interactables.sprites():
            collision_entity = pygame.sprite.spritecollideany(interactable,self.game_objects.players,Collisions.collided)
            if collision_entity:
                interactable.player_collision()
            else:
                interactable.player_noncollision()

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
            collision_inetractables = pygame.sprite.spritecollideany(projectile,self.game_objects.interactables,Collisions.collided)

            #if hit chest, bushes
            if collision_inetractables:
                projectile.collision_inetractables(collision_inetractables)

            #if hit enemy
            if collision_enemy:
                projectile.collision_enemy(collision_enemy)

            #hit platform
            if collision_plat:
                projectile.collision_plat(collision_plat)

    #check for player collision
    def player_collision(self,enteties):#loot and enemies: need to be sprite collide for loot so that you can pick up several ay pnce
        for player in self.game_objects.players:#aila and eventual double gangler
            collision_enteties = pygame.sprite.spritecollide(player,enteties,dokill = False, collided = Collisions.collided)#check collision
            for collision_entetiy in collision_enteties:
                collision_entetiy.player_collision(player)

    #npc player conversation, when pressing t
    def check_interaction_collision(self):
        npc =  pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.npcs,Collisions.collided)#check collision
        interactable = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.interactables,Collisions.collided)#check collision

        if npc:
            npc.interact()
        elif interactable:
            interactable.interact()

    #collision of player, enemy and loot: setting the flags depedning on the collisoin directions
    #collisions between entities-groups: a dynamic and a static one
    def platform_collision(self,dynamic_Entities):
        for entity in dynamic_Entities.sprites():
            entity.collision_types = {'top':False,'bottom':False,'right':False,'left':False}

            #move in x every dynamic sprite
            entity.update_true_pos_x()
            static_entity_x = pygame.sprite.spritecollideany(entity,self.game_objects.platforms,Collisions.collided)
            if static_entity_x:
                static_entity_x.collide_x(entity)

            #move in y every dynamic sprite
            entity.update_true_pos_y()
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

    @staticmethod
    def collided_point(dynamic_Entities,static_entities):
        return static_entities.hitbox.collidepoint(dynamic_Entities.hitbox.midbottom)
