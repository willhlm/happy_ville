import pygame

class Collisions():
    def __init__(self):
        self.shake=0

    def action_collision(self,projectiles,projectile_enteties,platforms,enemies,screen,loot,cosmetics):
        self.shake-=1
        self.shake=max(0,self.shake)#to not let it go to too low valyes

        for entity in projectile_enteties.sprites():#go through the group
            projectiles=entity.attack_action(projectiles)

            for projectile in projectiles.sprites():#go through the group

                #projectile collision?
                collision_plat = pygame.sprite.spritecollideany(projectile,platforms,Collisions.collided)
                collision_ene = pygame.sprite.spritecollideany(projectile,enemies,Collisions.collided)

                pygame.draw.rect(screen, (0,0,255), projectile.hitbox,2)#draw hitbox

                #if hit enemy
                if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:

                    collision_ene.health-=projectile.dmg
                    collision_ene.action['hurt']=True

                    self.shake=collision_ene.death(loot)#check if dead

                    projectile.collision(entity,cosmetics,collision_ene)#response of projetile hits

                #hit platform
                elif collision_plat:
                    projectile.collision(entity)#entity is the guy donig the action

    @staticmethod
    def collided(projectile,target):
        return projectile.hitbox.colliderect(target.hitbox)

    #take damage if collide with enemy
    @staticmethod
    def check_enemy_collision(player,enemies,loot):
        collided=Collisions.collided #make the hitbox collide and not rect
        collisions=pygame.sprite.spritecollideany(player,enemies,collided)#check collision
        if collisions and not player.action['hurt']:
            player.health-=10
            player.velocity[0]=-player.dir[0]*10#knock back of player (will not completly work)
            player.action['hurt']=True
            player.death(loot)#check if dead
        return loot

    #pickup loot
    @staticmethod
    def pickup_loot(player,loots):
        collided=Collisions.collided #make the hitbox collide and not rect
        collision=pygame.sprite.spritecollide(player,loots,True,collided)#check collision
        for loot in collision:
            obj=(loot.__class__.__name__)#get the loot in question
            player.loot[obj]+=1

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
    def check_invisible(dynamic_entities,inv_enteties):
        collided=Collisions.collided#make the hitbox collide and not rect

        collisions=pygame.sprite.groupcollide(dynamic_entities,inv_enteties,False,False,collided)
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

    #making the loot fall on platofrm
    @staticmethod
    def check_collisions_loot(loots,platforms):
        Collisions.collide(loots,platforms)

        for loot in loots:#if hit ground
            if loot.collision_types['bottom']:
                loot.velocity=[0,0]

    #collision of player and enemy: setting the flags depedning on the collisoin directions
    @staticmethod
    def check_collisions(dynamic_entities,platforms):
        Collisions.collide(dynamic_entities,platforms)

        for entity in dynamic_entities.sprites():

            entity.friction[1]=0

            if entity.collision_types['bottom']:#if on ground
                entity.dashing_cooldown=10

                entity.velocity[1]=0
                entity.action['fall']=False
                entity.action['stand']=True
                entity.action['wall']=False
                entity.action['jump']=False
                if entity.dir[1]<0:#if on ground, cancel sword swing
                    entity.action['sword']=False
            else:#if not on ground
                entity.action['stand']=False
                if entity.velocity[1]>=0:#if falling down
                    entity.action['jump']=False
                    entity.action['fall']=True
                    if entity.collision_types['right'] or entity.collision_types['left']:#on wall and not on ground
                        entity.action['wall']=True
                        entity.action['dash']=False
                        entity.action['fall']=False
                        entity.friction[1]=0.4
                        entity.dashing_cooldown=10
                    else:
                        entity.action['wall']=False
                else:#if going up
                    entity.action['jump']=True

            if entity.collision_types['top']:#knock back when hit head
                entity.velocity[1]=0

            if entity.collision_spikes['bottom']:
                entity.action['hurt']=True
                entity.velocity[1]=-6
                entity.health-=10
                if entity.health<=0:
                    entity.action['death']=True

    #collisions between enteties-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_entities,static_enteties):

        #move in x every dynamic sprite
        for entity in dynamic_entities.sprites():
            entity.rect.center = [round(entity.rect.center[0] + entity.movement[0]), entity.rect.center[1]]
            entity.update_hitbox()
            entity.collision_types={'top':False,'bottom':False,'right':False,'left':False}
            entity.collision_spikes={'top':False,'bottom':False,'right':False,'left':False}

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entities,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].hitbox.left
                dyn_entity.collision_types['right'] = True
                dyn_entity.collision_spikes['right'] = stat_entity[0].spike

            elif dyn_entity.movement[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].hitbox.right
                dyn_entity.collision_types['left'] = True
                dyn_entity.collision_spikes['left'] = stat_entity[0].spike

            dyn_entity.update_rect()

        #move in y every dynamic sprite
        for entity in dynamic_entities.sprites():
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.movement[1])]
            entity.update_hitbox()#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entities,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[1]>0:#going down
                dyn_entity.hitbox.bottom = stat_entity[0].hitbox.top
                dyn_entity.collision_types['bottom'] = True
                dyn_entity.collision_spikes['bottom'] = stat_entity[0].spike



            elif dyn_entity.movement[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[0].hitbox.bottom
                dyn_entity.collision_types['top'] = True
                dyn_entity.collision_spikes['top'] = stat_entity[0].spike

            dyn_entity.update_rect()

    #make the hitbox collide instead of rect
    @staticmethod
    def collided(dynamic_entities,static_enteties):
        return dynamic_entities.hitbox.colliderect(static_enteties.hitbox)
#
class Physics():
    def __init__(self):
        pass

    @staticmethod
    def movement(dynamic_entities):
        for entity in dynamic_entities.sprites():

            entity.velocity[1]=entity.velocity[1]+entity.acceleration[1]-entity.velocity[1]*entity.friction[1]#gravity
            entity.velocity[1]=min(entity.velocity[1],7)#set a y max speed

            if entity.action['dash']:
                entity.dashing_cooldown-=1
                entity.velocity[1]=0
                entity.velocity[0]=entity.velocity[0]+entity.ac_dir[0]*0.5

                if abs(entity.velocity[0])<10:#max horizontal speed
                    entity.velocity[0]=entity.ac_dir[0]*10
                #entity.velocity[0]=max(10,entity.velocity[0])
            try:
                if entity.action['run'] and not entity.charging[0]:#accelerate horizontal to direction when not dashing
                    entity.velocity[0]+=entity.dir[0]*entity.acceleration[0]
                    entity.friction[0]=0.2
                    if abs(entity.velocity[0])>10:#max horizontal speed
                        entity.velocity[0]=entity.dir[0]*10
            except:
                if entity.action['run']:#accelerate horizontal to direction when not dashing
                    entity.velocity[0]+=entity.dir[0]*entity.acceleration[0]
                    entity.friction[0]=0.2
                    if abs(entity.velocity[0])>entity.max_vel:#max horizontal speed
                        entity.velocity[0]=entity.dir[0]*entity.max_vel

            entity.movement[1]=entity.velocity[1]#set the vertical velocity

            entity.velocity[0]=entity.velocity[0]-entity.friction[0]*entity.velocity[0]#friction
            entity.movement[0]=entity.velocity[0]#set the horizontal velocity

class Animation():
    def __init__(self):
        #super().__init__()
        pass


    ### FIX frame rate thingy
    @staticmethod
    def set_img(enteties):

        for entity in enteties.sprites():#go through the group
            all_action=entity.priority_action+entity.nonpriority_action


            for action in all_action:#go through the actions
                if entity.action[action] and action in entity.priority_action:#if the action is priority

                    if action != entity.state:
                        entity.state = action
                        entity.reset_timer()

                    entity.image = entity.sprites.get_image(action,entity.frame//5,entity.ac_dir)
                    entity.frame += 1

                    if entity.frame == entity.sprites.get_frame_number(action,entity.ac_dir)*5:
                        if action == 'death':
                            entity.kill()
                        else:
                            entity.reset_timer()
                            entity.action[action] = False
                            entity.state = 'stand'
                            entity.action[entity.equip]=False#to cancel even if you get hurt

                    break

                elif entity.action[action] and action in entity.nonpriority_action:#if the action is nonpriority

                    #reset timer if the action is wrong
                    if action != entity.state:
                        entity.state = action
                        entity.reset_timer()

                    entity.image = entity.sprites.get_image(action,entity.frame//5,entity.dir)
                    entity.frame += 1

                    if entity.frame == entity.sprites.get_frame_number(action,entity.dir)*5:
                            entity.reset_timer()
                    break#take only the higest priority of the nonpriority list
