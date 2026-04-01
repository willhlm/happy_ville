import pygame, math

class Collisions():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self._collision_state = {}  # target → {entities}

    def _is_collidable(self, entity):
        platform_physics = getattr(entity, "platform_physics", None)
        if platform_physics:
            return platform_physics.can_collide()
        return True

    def check_ground(self, point):#called from AI
        for platform in self.game_objects.platforms:
            if platform.hitbox.collidepoint(point):
                return True
        return False

    def pass_through(self, entity):#called when pressing down
        hitbox = entity.hitbox.copy()
        offset = 1#looks better if it is 1, but if it is 1, the fall through doesn't work when going dow the ramp
        hitbox.bottom += offset

        ramp = None
        for ramps in self.game_objects.platforms_ramps.sprites():
            if hitbox.colliderect(ramps.hitbox):
                ramp = ramps
                break

        if ramp:
            target = ramp.get_target(entity)#in case there are multiple enteties, need to calcuate the tyarget specifically for the playter
            if target > hitbox.bottom + offset:
                return #if from above, do nothing
            elif not entity.go_through['ramp']:#enter only once
                entity.velocity[1] = offset#so that it looks more natural (cannot be 0, needs to be finite)
                entity.go_through['ramp'] = ramp.go_through#a flag that determines if one can go through

    #npc player conversation, when pressing t
    def check_interaction_collision(self):
        npc =  pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.npcs,Collisions.collided)#check collision
        interactable = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.interactables,Collisions.collided)#check collision
        loot = pygame.sprite.spritecollideany(self.game_objects.player,self.game_objects.loot,Collisions.collided)#check collision

        if npc:
            npc.interact()
        elif interactable:
            interactable.interact()
        elif loot:
            loot.interact(self.game_objects.player)

    def entity_collision(self, entities, target_group):
        """
        Track collisions using object references.
        - on_collision(entity): called ONCE when entity enters, before first collision(entity)
        - collision(entity): called EVERY frame while colliding
        - on_noncollision(entity): called ONCE when entity exits
        """
        is_collidable = self._is_collidable
        collided = self.collided
        collision_state = self._collision_state

        for target in target_group:
            previous = collision_state.get(target, set())
            current = set()

            # Find current collisions
            for entity in entities:
                if not is_collidable(entity):
                    continue
                if collided(entity, target):
                    if entity not in previous:
                        target.on_collision(entity)
                    target.collision(entity)
                    current.add(entity)

            # Calculate state changes
            exited = previous - current

            # Emit events
            for entity in exited:#once
                #if target.alive():
                target.on_noncollision(entity)

            # Update state
            if current:
                collision_state[target] = current
            elif target in collision_state:
                del collision_state[target] 

    #check for entity collision
    def simple_collision(self, entities, target_group, callback_name = 'collision'):
        """
        Generic collision check that calls a named method on targets.
        
        Args:
            entities: Group of entities to check
            target_group: Group of targets
            callback_name: Method name to call on target (default: 'collision')
        """
        is_collidable = self._is_collidable
        collided = Collisions.collided

        for entity in entities.sprites():
            if not is_collidable(entity):
                continue
            collision_targets = pygame.sprite.spritecollide(entity, target_group, dokill=False, collided=collided)
            for target in collision_targets:
                callback = getattr(target, callback_name)
                callback(entity)

    #collision of player, enemy and loot: setting the flags depedning on the collisoin directions collisions between entities-groups: a dynamic and a static one    
    def platform_collision(self, dynamic_Entities, dt):
        platforms = self.game_objects.platforms
        ramps = self.game_objects.platforms_ramps

        for entity in dynamic_Entities:
            if not self._is_collidable(entity):
                continue
            self._begin_platform_step(entity)
            entity_dt = entity.hitstop.get_sim_dt(dt)
            if self._resolve_platform_axis_x(entity, entity_dt, platforms):
                continue
            if self._resolve_platform_axis_y(entity, entity_dt, platforms):
                continue
            self._resolve_ramps(entity, ramps)

    def _begin_platform_step(self, entity):
        entity.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        entity.old_hitbox = entity.hitbox.copy()
        if entity.standing_platform:
            entity.standing_platform.pre_entity_y_collision(entity)

    def _resolve_platform_axis_x(self, entity, entity_dt, platforms):
        entity.body.update_true_pos_x(entity_dt)
        colliders = self._gather_platform_colliders(entity, platforms)
        if entity.velocity[0] != 0 and self._handle_crush(entity, colliders, axis='x'):
            return True
        self._resolve_platform_colliders(entity, colliders, axis='x')
        return False

    def _resolve_platform_axis_y(self, entity, entity_dt, platforms):
        entity.body.update_true_pos_y(entity_dt)
        colliders = self._gather_platform_colliders(entity, platforms)
        if entity.velocity[1] != 0 and self._handle_crush(entity, colliders, axis='y'):
            return True
        self._resolve_platform_colliders(entity, colliders, axis='y')
        return False

    def _gather_platform_colliders(self, entity, platforms):
        return pygame.sprite.spritecollide(entity, platforms, False, Collisions.collided)

    def _resolve_platform_colliders(self, entity, colliders, axis):
        for platform in colliders:
            getattr(platform, f'collide_{axis}')(entity)

    def _resolve_ramps(self, entity, ramps_group):
        ramps = pygame.sprite.spritecollide(entity, ramps_group, False, Collisions.collided)
        if ramps:
            for ramp in ramps:
                ramp.collide(entity)
        else:
            entity.go_through['ramp'] = False

    def _handle_crush(self, entity, colliders, axis):
        if len(colliders) < 2:
            return False

        if not any(getattr(platform, 'delta', [0, 0]) != [0, 0] for platform in colliders):
            return False

        for platform in colliders:
            if not hasattr(platform, 'delta'):
                continue

            dx, dy = platform.delta
            if dx == 0 and dy == 0:
                continue

            if axis == 'y' and dy > 0 and entity.platform_physics.is_crushed(platform, 'top'):
                entity.platform_physics.handle_crush(platform)
                return True
            if axis == 'y' and dy < 0 and entity.platform_physics.is_crushed(platform, 'bottom'):
                entity.platform_physics.handle_crush(platform)
                return True
            if axis == 'x' and dx > 0 and entity.platform_physics.is_crushed(platform, 'left'):
                entity.platform_physics.handle_crush(platform)
                return True
            if axis == 'x' and dx < 0 and entity.platform_physics.is_crushed(platform, 'right'):
                entity.platform_physics.handle_crush(platform)
                return True

        return False

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
