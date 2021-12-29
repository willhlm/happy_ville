import pygame

class Collisions():
    def __init__(self):
        self.shake=0

    @staticmethod
    def weather_paricles(weathers,platforms):

        collisions=pygame.sprite.groupcollide(weathers,platforms,False,False)
        for weather, platform in collisions.items():
            weather.collision()

    def action_collision(self,projectiles,platforms,enemies):
        self.shake-=1
        self.shake=max(0,self.shake)#to not let it go to too low values

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

        collision=pygame.sprite.spritecollide(player,loots,True,Collisions.collided)#check collision
        for loot in collision:
            obj=(loot.__class__.__name__)#get the loot in question
            player.inventory[obj]+=1

    #npc player conversation
    @staticmethod
    def check_npc_collision(player,npcs):
        return pygame.sprite.spritecollideany(player,npcs)#check collision

    #invisible wall collision for NPC and enemy
    @staticmethod
    def check_invisible(dynamic_Entities,inv_enteties):

        collisions=pygame.sprite.groupcollide(dynamic_Entities,inv_enteties,False,False,Collisions.collided)
        for dyn_entity, inv_entity in collisions.items():
            dyn_entity.dir=-dyn_entity.dir#turn around

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
            entity.rect.center = [round(entity.rect.center[0] + entity.velocity[0]), entity.rect.center[1]]
            entity.update_hitbox()
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}

        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_Entities,static_enteties,False,False,Collisions.collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.velocity[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].hitbox.left
                dyn_entity.collision_types['right'] = True

            elif dyn_entity.velocity[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].hitbox.right
                dyn_entity.collision_types['left'] = True

            dyn_entity.update_rect()

        #move in y every dynamic sprite
        for entity in dynamic_Entities.sprites():
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.velocity[1])]
            entity.update_hitbox()#follow with hitbox

        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_Entities,static_enteties,False,False,Collisions.collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.velocity[1]>0:#going down
                dyn_entity.hitbox.bottom = stat_entity[0].hitbox.top
                dyn_entity.collision_types['bottom'] = True

            elif dyn_entity.velocity[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[0].hitbox.bottom
                dyn_entity.collision_types['top'] = True

            dyn_entity.update_rect()

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_enteties):
        return dynamic_Entities.hitbox.colliderect(static_enteties.hitbox)
