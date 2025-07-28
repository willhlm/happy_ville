import pygame, math

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects

    def check_ground(self, point):#called from AI
        for platform in self.game_objects.platforms:
            if platform.hitbox.collidepoint(point):
                return True
        return False

    def pass_through(self, entity):#called when pressing down
        hitbox = self.game_objects.player.hitbox.copy()
        offset = 1/self.game_objects.game.dt#looks better if it is 1, but if it is 1, the fall through doesn't work when going dow the ramp
        hitbox.bottom += offset

        ramp = None
        for ramps in self.game_objects.platforms_ramps.sprites():
            if hitbox.colliderect(ramps.hitbox):
                ramp = ramps
                break

        if ramp:
            target = ramp.get_target(self.game_objects.player)#in case there are multiple enteties, need to calcuate the tyarget specifically for the playter
            if target > hitbox.bottom + offset:
                return #if from above, do nothing
            elif not self.game_objects.player.go_through['ramp']:#enter only once
                self.game_objects.player.velocity[1] = offset#so that it looks more natural (cannot be 0, needs to be finite)
                self.game_objects.player.go_through['ramp'] = ramp.go_through#a flag that determines if one can go through

    def interactables_collision(self, enteties):#interactables
        for interactable in self.game_objects.interactables.sprites():
            collision_entity = pygame.sprite.spritecollideany(interactable, enteties, Collisions.collided)
            if collision_entity:
                interactable.player_collision(collision_entity)
            else:
                interactable.player_noncollision()

        for interactable in self.game_objects.interactables_fg.sprites():
            collision_entity = pygame.sprite.spritecollideany(interactable, enteties, Collisions.collided)
            if collision_entity:
                interactable.player_collision(collision_entity)
            else:
                interactable.player_noncollision()

    @staticmethod
    def counter(fprojectiles, eprojectiles):
        for projectile in fprojectiles.sprites():#go through the group
            collision_epro = pygame.sprite.spritecollideany(projectile, eprojectiles, Collisions.collided)
            if collision_epro:
                projectile.collision_projectile(collision_epro)

    def projectile_collision(self, projectiles, enemies):
        for projectile in projectiles.sprites():#go through the group
            #projectile collision?            
            collision_enemies = pygame.sprite.spritecollide(projectile, enemies, False, Collisions.collided)
            collision_interactables = pygame.sprite.spritecollideany(projectile, self.game_objects.interactables, Collisions.collided)
            collision_interactables_fg = pygame.sprite.spritecollideany(projectile, self.game_objects.interactables_fg, Collisions.collided)
            
            #if hit chest, bushes
            if collision_interactables:
                projectile.collision_interactables(collision_interactables)#go through the projecticle in case there are projectile that should do dmg to interactable

            #if hit e.g. twoDliquid
            if collision_interactables_fg:
                projectile.collision_interactables_fg(collision_interactables_fg)

            #if hit enemy
            for enemy in collision_enemies:
                projectile.collision_enemy(enemy)

    #check for player collision
    def player_collision(self, enteties):#loot and enemies: need to be sprite collide for loot so that you can pick up several ay pnce
        for player in self.game_objects.players:#aila and eventual double gangler
            collision_enteties = pygame.sprite.spritecollide(player,enteties,dokill = False, collided = Collisions.collided)#check collision
            for collision_entetiy in collision_enteties:
                collision_entetiy.player_collision(player)

    #npc player conversation, when pressing t
    def check_interaction_collision(self):
        npc =  pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.npcs,Collisions.collided)#check collision
        interactable = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.interactables,Collisions.collided)#check collision
        loot = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.loot,Collisions.collided)#check collision

        if npc:
            npc.interact()
        elif interactable:
            interactable.interact()
        if loot:
            loot.interact(self.game_objects.player)

    #collision of player, enemy and loot: setting the flags depedning on the collisoin directions
    #collisions between entities-groups: a dynamic and a static one
    def platform_collision(self, dynamic_Entities, dt):
        for entity in dynamic_Entities.sprites():
            entity.collision_types = {'top':False,'bottom':False,'right':False,'left':False, 'standing_platform': None}
            
            #move in x every dynamic sprite            
            entity.old_hitbox = entity.hitbox.copy()#save old position
            entity.update_true_pos_x(dt)#it sets the true pos and update the hitbox
            static_entities_x = pygame.sprite.spritecollide(entity, self.game_objects.platforms, False, Collisions.collided)
            for static_entity_x in static_entities_x:                
                static_entity_x.collide_x(entity)

            #move in y every dynamic sprite
            entity.update_true_pos_y(dt)#it sets the true pos and update the hitbox              
            static_entities_y = pygame.sprite.spritecollide(entity, self.game_objects.platforms, False, Collisions.collided)                        
            for static_entity_y in static_entities_y:                
                static_entity_y.collide_y(entity)

            ramps = pygame.sprite.spritecollide(entity,self.game_objects.platforms_ramps,False,Collisions.collided)
            if ramps:
                for ramp in ramps:
                    ramp.collide(entity)
            else:
                entity.go_through['ramp'] = False       

    def sprite_collide(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, Collisions.collided)

    def sprite_collide_any(self, sprite, group):
        return pygame.sprite.spritecollideany(sprite, group, Collisions.collided)

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities, static_entities):
        return dynamic_Entities.hitbox.colliderect(static_entities.hitbox)

    @staticmethod
    def collided_point(dynamic_Entities, static_entities):
        return static_entities.hitbox.collidepoint(dynamic_Entities.hitbox.midbottom)
