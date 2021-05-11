import pygame

class Collisions():
    def __init__(self):
        pass

    #npc player conversation
    @staticmethod
    def check_npc_collision(player,npcs,screen):
        npc=pygame.sprite.spritecollideany(player,npcs)#check collision
        if npc and player.action['talk']==True:#if player want to talk talks
            npc.talk(screen,player)
            player.state='talk'#the player talks

    #invisible wall collision for NPC and enemy
    @staticmethod
    def check_invisible(dynamic_entities,inv_enteties):
        collided=Collisions.collided#make the hitbox collide and not rect

        collisions=pygame.sprite.groupcollide(dynamic_entities,inv_enteties,False,False,collided)
        for dyn_entity, inv_entity in collisions.items():
            dyn_entity.action['inv']=True

    #collision of player and enemy: setting the flags depedning on the collisoin directions
    @staticmethod
    def check_collisions(dynamic_entities,platforms):
        collision_types=Collisions.collide(dynamic_entities,platforms)

        for entity in dynamic_entities.sprites():

            entity.friction[1]=0

            if collision_types['bottom']:#if on ground
                entity.velocity[1]=0
                entity.action['fall']=False
                entity.action['stand']=True
                entity.action['wall']=False
                if entity.dir[1]<0:#if on ground, cancel sword swing
                    entity.action['sword']=False
            else:#if not on ground
                entity.action['stand']=False
                if entity.velocity[1]>0:#if falling down
                    entity.action['jump']=False
                    entity.action['fall']=True
                    if collision_types['right'] or collision_types['left']:#on wall and not on ground
                        entity.action['wall']=True
                        entity.action['fall']=False
                        entity.friction[1]=0.4
                    else:
                        entity.action['wall']=False
                else:#if going up
                    entity.action['jump']=True

            if collision_types['top']:#knock back when hit head
                entity.velocity[1]=0


    #collisions between enteties-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_entities,static_enteties):
        collision_types = {'top':False,'bottom':False,'right':False,'left':False}

        #move in x every dynamic sprite
        for entity in dynamic_entities.sprites():
            entity.rect.center = [round(entity.rect.center[0] + entity.movement[0]), entity.rect.center[1]]
            entity.update_hitbox()

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entities,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].hitbox.left
                collision_types['right'] = True

            elif dyn_entity.movement[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].hitbox.right
                collision_types['left'] = True
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
                dyn_entity.hitbox.bottom = stat_entity[-1].hitbox.top
                collision_types['bottom'] = True

            elif dyn_entity.movement[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[-1].hitbox.bottom
                collision_types['top'] = True
            dyn_entity.update_rect()

        return collision_types

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
            if entity.velocity[1]>7:#set a y max speed
                entity.velocity[1]=7
            entity.movement[1]=entity.velocity[1]#set the vertical velocity

            if entity.action['run'] and not entity.action['dash']:#accelerate horizontal to direction when not dashing
                entity.velocity[0]+=entity.dir[0]*entity.acceleration[0]

                if abs(entity.velocity[0])>10:#max horizontal speed
                    entity.velocity[0]=entity.dir[0]*10

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
            for action in entity.priority_action+entity.nonpriority_action:#go through the group
                if entity.action[action] and action in entity.priority_action:#if the action is priority
                    if action != entity.state:
                        entity.state = action
                        entity.reset_timer()

                    entity.image = entity.sprites.get_image(action,entity.frame//3,entity.ac_dir)
                    entity.frame += 1

                    if entity.frame == entity.sprites.get_frame_number(action,entity.ac_dir)*3:
                        if action == 'death':
                            entity.kill()
                        else:
                            entity.reset_timer()
                            entity.action[action] = False
                            entity.f_action_cooldown=True
                    break

                elif entity.action[action] and action in entity.nonpriority_action:#if the action is nonpriority

                    #reset timer if the action is wrong
                    if action != entity.state:
                        entity.state = action
                        entity.reset_timer()

                    entity.image = entity.sprites.get_image(action,entity.frame//3,entity.dir)
                    entity.frame += 1

                    if entity.frame == entity.sprites.get_frame_number(action,entity.dir)*3:
                            entity.reset_timer()
                    break#take only the higest priority of the nonpriority list
