import pygame

class Collisions():
    def __init__(self):
        self.shake=0

    def action_collision(self,projectiles,projectile_enteties,platforms,enemies,screen,loot,cosmetics):
        self.shake-=1
        self.shake=max(0,self.shake)#to not let it go to too low values

        for entity in projectile_enteties.sprites():#go through the group
            projectiles=entity.attack_action(projectiles)

            for projectile in projectiles.sprites():#go through the group

                #projectile collision?
                collision_plat = pygame.sprite.spritecollideany(projectile,platforms,Collisions.collided)
                collision_ene = pygame.sprite.spritecollideany(projectile,enemies,Collisions.collided)

                pygame.draw.rect(screen, (0,0,255), projectile.hitbox,2)#draw hitbox

                #if hit enemy
                if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:

                    #self.shake+=collision_ene.death(loot)#check if dead
                    collision_ene.take_dmg(projectile.dmg)
                    self.shake=projectile.collision(entity,cosmetics,collision_ene)#response of projetile hits

                    if collision_ene.action['death']:
                        self.shake+=collision_ene.shake
                        loot.add(collision_ene.loots())

                #hit platform
                elif collision_plat:
                    self.shake=projectile.collision(entity)#entity is the guy donig the action

    @staticmethod
    def collided(projectile,target):
        return projectile.hitbox.colliderect(target.hitbox)

    #take damage if collide with enemy
    @staticmethod
    def check_enemy_collision(player,enemies):
        collided=Collisions.collided #make the hitbox collide and not rect
        collisions=pygame.sprite.spritecollideany(player,enemies,collided)#check collision

        if collisions and not player.action['hurt'] and not collisions.action['death']:
            player.take_dmg(10)

            sign=(player.hitbox.center[0]-collisions.hitbox.center[0])/(abs(player.hitbox.center[0]-collisions.hitbox.center[0]))
            #if player.hitbox.center[0] > collisions.hitbox.center[0]:#player on right
            player.velocity[0]=sign*10#knock back of player
        #    else:#player on left
            #    player.velocity[0]=-10#knock back of player

    #pickup loot
    @staticmethod
    def pickup_loot(player,loots):
        collided=Collisions.collided #make the hitbox collide and not rect
        collision=pygame.sprite.spritecollide(player,loots,True,collided)#check collision
        for loot in collision:
            obj=(loot.__class__.__name__)#get the loot in question
            player.inventory[obj]+=1

    #npc player conversation
    @staticmethod
    def check_npc_collision(player,npcs):
        npc=pygame.sprite.spritecollideany(player,npcs)#check collision
        if npc and player.action['talk']==True:#if player want to talk talks
            #npc.talk(screen,player)
            player.state='talk'#the player talks with npc
            player.action['run']=False
            npc.action['talk'] = True
            return npc

        #return None if no interaction
        return

    #invisible wall collision for NPC and enemy
    @staticmethod
    def check_invisible(dynamic_Entities,inv_enteties):
        collided=Collisions.collided#make the hitbox collide and not rect

        collisions=pygame.sprite.groupcollide(dynamic_Entities,inv_enteties,False,False,collided)
        for dyn_entity, inv_entity in collisions.items():
            dyn_entity.action['inv']=True

    #interact with chests
    @staticmethod
    def check_interaction(player,static_enteties):
        map_change = False
        chest_id = False
        if player.interacting:
            collided=Collisions.collided #make the hitbox collide and not rect
            collision=pygame.sprite.spritecollideany(player,static_enteties,collided)#check collision
            if collision:
                collision.interacted = True
                if type(collision).__name__ == "Door":
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
        collided = Collisions.collided
        collision = pygame.sprite.spritecollideany(player,triggers,collided)
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
            entity.rect.center = [round(entity.rect.center[0] + entity.movement[0]), entity.rect.center[1]]
            entity.update_hitbox()
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_Entities,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].hitbox.left
                dyn_entity.collision_types['right'] = True

            elif dyn_entity.movement[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].hitbox.right
                dyn_entity.collision_types['left'] = True

            dyn_entity.update_rect()

        #move in y every dynamic sprite
        for entity in dynamic_Entities.sprites():
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.movement[1])]
            entity.update_hitbox()#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_Entities,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[1]>0:#going down
                dyn_entity.hitbox.bottom = stat_entity[0].hitbox.top
                dyn_entity.collision_types['bottom'] = True

            elif dyn_entity.movement[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[0].hitbox.bottom
                dyn_entity.collision_types['top'] = True

            dyn_entity.update_rect()

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_Entities,static_enteties):
        return dynamic_Entities.hitbox.colliderect(static_enteties.hitbox)
