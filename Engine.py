import pygame

class Collisions():
    def __init__(self):
        self.shake=0

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
        collisions=pygame.sprite.groupcollide(weathers,platforms,False,False)
        for weather, platform in collisions.items():
            weather.collision()

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
                #self.shake+=collision_enemy.death(loot)#check if dead
                #self.shake=projectile.collision(entity,cosmetics,collision_enemy)#response of projetile hits

                #if collision_enemy.action['death']:
                #    self.shake+=collision_enemy.shake
                #    loot.add(collision_enemy.loots())

            #hit platform
            elif collision_plat:
                projectile.collision_plat()
                #self.shake=projectile.collision(entity)#entity is the guy donig the action

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
    #    for loot in collision:
            collision_loot.pickup(player)
            #if obj=='Spiritsorb':
            #    player.spirit += 10

            #else:
            #    player.inventory[obj]+=1

    #npc player conversation
    @staticmethod
    def check_npc_collision(player,npcs):
        return pygame.sprite.spritecollideany(player,npcs)#check collision

    #invisible wall collision for NPC and enemy
    @staticmethod
    def check_invisible(dynamic_Entities,inv_entities):

        collisions=pygame.sprite.groupcollide(dynamic_Entities,inv_entities,False,False,Collisions.collided)
        for dyn_entity, inv_entity in collisions.items():
            dyn_entity.dir[0]=-dyn_entity.dir[0]#turn around

    #interact with chests
    @staticmethod
    def check_interaction(player,static_entities):
        map_change = False
        chest_id = False
        collision=pygame.sprite.spritecollideany(player,static_entities,Collisions.collided)#check collision
        if collision:
            collision.interacted = True
            if type(collision).__name__ == "Door":
                print('before try')
                try:
                    map_change = collision.next_map
                except:
                    pass
            if type(collision).__name__ in ["Chest", "Chest_Big"]:
                try:
                    chest_id = collision.ID
                except:
                    pass

        return map_change, chest_id

    @staticmethod
    def check_trigger(player,triggers):
        map_change = False
        collision = pygame.sprite.spritecollideany(player,triggers,Collisions.collided)
        if collision:
            if type(collision).__name__ in ["Path_Col_h","Path_Col_v"]:
                try:
                    map_change = collision.next_map
                except:
                    pass

        return map_change

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

                #check for collisions and get a dictionary of sprites that collides
                if entity.velocity[0]>0:#going to the right
                    entity.hitbox.right = static_entity_x.hitbox.left
                    entity.collision_types['right'] = True

                elif entity.velocity[0]<0:#going to the left
                    entity.hitbox.left = static_entity_x.hitbox.right
                    entity.collision_types['left'] = True
                entity.update_rect()

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

                    if entity.velocity[1]>0:#going down
                        entity.hitbox.bottom = static_entity_y.hitbox.top
                        entity.collision_types['bottom'] = True

                    elif entity.velocity[1]<0:#going up
                        entity.hitbox.top = static_entity_y.hitbox.bottom
                        entity.collision_types['top'] = True
                    entity.update_rect()

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_entities):
        return dynamic_Entities.hitbox.colliderect(static_entities.hitbox)
