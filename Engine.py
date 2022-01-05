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
                    collision_epro.conutered()

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
            collision_ene = pygame.sprite.spritecollideany(projectile,enemies,Collisions.collided)

            #if hit enemy
            if collision_ene:# and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                if str(type(collision_ene.currentstate).__name__) is not 'Hurt':
                #self.shake+=collision_ene.death(loot)#check if dead
                    collision_ene.take_dmg(projectile.dmg)
                    projectile.collision_ene(collision_ene)
                #self.shake=projectile.collision(entity,cosmetics,collision_ene)#response of projetile hits

                #if collision_ene.action['death']:
                #    self.shake+=collision_ene.shake
                #    loot.add(collision_ene.loots())

            #hit platform
            elif collision_plat:
                projectile.collision_plat()
                #self.shake=projectile.collision(entity)#entity is the guy donig the action

    #take damage if collide with enemy
    @staticmethod
    def check_enemy_collision(player,enemies):
        collision_ene=pygame.sprite.spritecollideany(player,enemies,Collisions.collided)#check collision

        if collision_ene:
            if str(type(collision_ene.currentstate).__name__) is not 'Death':

                player.take_dmg(10)
                sign=(player.hitbox.center[0]-collision_ene.hitbox.center[0])
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
    def check_invisible(dynamic_Entities,inv_enteties):

        collisions=pygame.sprite.groupcollide(dynamic_Entities,inv_enteties,False,False,Collisions.collided)
        for dyn_entity, inv_entity in collisions.items():
            dyn_entity.dir[0]=-dyn_entity.dir[0]#turn around

    #interact with chests
    @staticmethod
    def check_interaction(player,static_enteties):
        map_change = False
        chest_id = False
        collision=pygame.sprite.spritecollideany(player,static_enteties,Collisions.collided)#check collision
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
    #collisions between enteties-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_Entities,static_enteties):

        #move in x every dynamic sprite
        for entity in dynamic_Entities.sprites():
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}

            entity.rect.center = [round(entity.rect.center[0] + entity.velocity[0]), entity.rect.center[1]]
            entity.update_hitbox()

            collision_x = pygame.sprite.spritecollideany(entity,static_enteties,Collisions.collided)

            if collision_x:
                #check for collisions and get a dictionary of sprites that collides
                if entity.velocity[0]>0:#going to the right
                    entity.hitbox.right = collision_x.hitbox.left
                    entity.collision_types['right'] = True

                elif entity.velocity[0]<0:#going to the left
                    entity.hitbox.left = collision_x.hitbox.right
                    entity.collision_types['left'] = True

                entity.update_rect()

            #move in y every dynamic sprite
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.velocity[1])]
            entity.update_hitbox()#follow with hitbox

            collision_y = pygame.sprite.spritecollideany(entity,static_enteties,Collisions.collided)

            if collision_y:

                if entity.velocity[1]>0:#going down
                    entity.hitbox.bottom = collision_y.hitbox.top
                    entity.collision_types['bottom'] = True

                elif entity.velocity[1]<0:#going up
                    entity.hitbox.top = collision_y.hitbox.bottom
                    entity.collision_types['top'] = True

                entity.update_rect()

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_enteties):
        return dynamic_Entities.hitbox.colliderect(static_enteties.hitbox)
