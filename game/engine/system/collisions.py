import pygame, math

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self._collision_state = {}  # target → {entities}

    def check_ground(self, point):#called from AI
        for platform in self.game_objects.platforms:
            if platform.hitbox.collidepoint(point):
                return True
        return False

    def pass_through(self, entity):#called when pressing down
        hitbox = self.game_objects.player.hitbox.copy()
        offset = 1#looks better if it is 1, but if it is 1, the fall through doesn't work when going dow the ramp
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

    def entity_collision(self, entities, target_group):
        """
        Track collisions using object references.
        - collision(entity): called EVERY frame while colliding
        - on_collision(entity): called ONCE when entity enters
        - on_noncollision(entity): called ONCE when entity exits
        """
        entity_list = list(entities.sprites())
        active_targets = set(target_group.sprites())

        for target in active_targets:
            previous = self._collision_state.get(target, set())
            current = set()

            # Find current collisions
            for entity in entity_list:
                if self.collided(entity, target):
                    target.collision(entity)
                    current.add(entity)

            # Calculate state changes
            entered = current - previous
            exited = previous - current

            # Emit events
            for entity in entered:#once
                #if target.alive():
                target.on_collision(entity)

            for entity in exited:#once
                #if target.alive():
                target.on_noncollision(entity)

            # Update state
            if current:
                self._collision_state[target] = current
            elif target in self._collision_state:
                del self._collision_state[target] 

    #check for entity collision
    def simple_collision(self, entities, target_group, callback_name = 'collision'):
        """
        Generic collision check that calls a named method on targets.
        
        Args:
            entities: Group of entities to check
            target_group: Group of targets
            callback_name: Method name to call on target (default: 'collision')
        """
        for entity in entities.sprites():
            collision_targets = pygame.sprite.spritecollide(entity, target_group, dokill=False, collided=Collisions.collided)
            for target in collision_targets:
                callback = getattr(target, callback_name)
                callback(entity)

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

    #collision of player, enemy and loot: setting the flags depedning on the collisoin directions collisions between entities-groups: a dynamic and a static one    
    def platform_collision(self, dynamic_Entities, dt):
        for entity in dynamic_Entities.sprites():
            entity.collision_types = {'top':False,'bottom':False,'right':False,'left':False, 'standing_platform': None}
            
            #move in x every dynamic sprite            
            entity.old_hitbox = entity.hitbox.copy()#save old position
            
            entity_dt = entity.get_sim_dt(dt)#hitstop can set it to 0
            entity.update_true_pos_x(entity_dt)#it sets the true pos and update the hitbox
            static_entities_x = pygame.sprite.spritecollide(entity, self.game_objects.platforms, False, Collisions.collided)
            for static_entity_x in static_entities_x:                
                static_entity_x.collide_x(entity)            

            #move in y every dynamic sprite
            entity.update_true_pos_y(entity_dt)#it sets the true pos and update the hitbox              
            static_entities_y = pygame.sprite.spritecollide(entity, self.game_objects.platforms, False, Collisions.collided)                        
            for static_entity_y in static_entities_y:                
                static_entity_y.collide_y(entity)

            ramps = pygame.sprite.spritecollide(entity, self.game_objects.platforms_ramps, False, Collisions.collided)
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

    def clear_state(self):
        self._collision_state.clear()




#def multi_target_collision(self, entities, targets_map):
#    """
#    Args:
#        entities: Group of entities to check
#        targets_map: Dict of {target_group: callback_name}
#    """
#    for entity in entities.sprites():
#        for target_group, callback_name in targets_map.items():
#            collision_targets = pygame.sprite.spritecollide(
#                entity, target_group, dokill=False, collided=Collisions.collided
#            )
#            for target in collision_targets:
#                callback = getattr(target, callback_name, None)
#                if callback:
#                    callback(entity)

# Usage:
#self.collisions.multi_target_collision(self.fprojectiles, {
#    self.eprojectiles: 'collision_projectile',
#    self.enemies: 'collision_enemy',
#    self.interactables: 'collision_interactables',
#    self.interactables_fg: 'collision_interactables_fg',
#})        