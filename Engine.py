import pygame

class Collisions():
    def __init__(self):
        pass

    @staticmethod
    def check_collisions(dynamic_entties,platforms):
        collision_types=Collisions.collide(dynamic_entties,platforms)

        for entity in dynamic_entties.sprites():
            if collision_types['bottom']:
                entity.action['jump']=False
                if entity.dir[1]<0:#if on ground, cancel sword swing
                    entity.action['sword']=False
                    entity.frame['sword']=1
            elif not collision_types['bottom']:
                entity.action['jump']=True
            elif collision_types['top']:#knock back when hit head
                entity.movement[1]=1

    #collisions between enteties-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_entties,static_enteties):
        collision_types = {'top':False,'bottom':False,'right':False,'left':False}

        #move in x every dynamic sprite
        for entity in dynamic_entties.sprites():
            entity.rect.center = [round(entity.rect.center[0] + entity.movement[0]), entity.rect.center[1] + 0]
            entity.hitbox.center = entity.rect.center#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entties,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].rect.left
                collision_types['right'] = True

            elif dyn_entity.movement[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].rect.right
                collision_types['left'] = True
            dyn_entity.rect.center=dyn_entity.hitbox.center

        #move in y every dynamic sprite
        for entity in dynamic_entties.sprites():
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.movement[1])]
            entity.hitbox.center = entity.rect.center#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entties,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[1]>0:#going down
                dyn_entity.hitbox.bottom = stat_entity[-1].rect.top
                collision_types['bottom'] = True

            elif dyn_entity.movement[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[-1].rect.bottom
                collision_types['top'] = True
            dyn_entity.rect.center=dyn_entity.hitbox.center

        return collision_types

    @staticmethod
    def collided(dynamic_entties,static_enteties):
        return dynamic_entties.hitbox.colliderect(static_enteties.rect)

class Physics():
    def __init__(self):
        pass

    @staticmethod
    def movement(dynamic_entties):
        for entity in dynamic_entties.sprites():
            entity.movement[1]+=entity.acceleration[1]#gravity
            if entity.movement[1]>5:#set a y max speed
                entity.movement[1]=5

            if entity.action['run'] and entity.dir[0]>0:#accelerate right
                entity.velocity[0]+=entity.acceleration[0]
                if entity.velocity[0]>10:#max speed
                    entity.velocity[0]=10
            elif entity.action['run'] and entity.dir[0]<0:#accelerate left
                entity.velocity[0]+=-entity.acceleration[0]
                if entity.velocity[0]<-10:#max speed
                    entity.velocity[0]=-10

            entity.velocity[0]=entity.velocity[0]-entity.friction*entity.velocity[0]#friction
            entity.movement[0]=entity.velocity[0]#set the horizontal velocity

class Animation():
    def __init__(self):
        #super().__init__()
        pass

    @staticmethod
    def set_img(enteties):
        for entity in enteties.sprites():#go through the group

            #need to order according to priority

            if not entity.action['death']:#if not dead
                if entity.action['dmg']:#if took dmg
                    entity.image=entity.images[entity.frame['dmg']//10+36]
                    entity.frame['dmg']+=1

                #reset frames
                    if entity.frame['dmg']==entity.frame_timer['dmg']:
                        entity.frame['dmg']=1
                        entity.action['dmg']=False

                elif entity.action['sword']:#sword
                    if entity.dir[1]>0 and entity.dir[0]>0:#sword up-right
                        entity.image=entity.images_sword[entity.frame['sword']//3+13]
                        entity.frame['sword']+=1
                    elif entity.dir[1]>0 and entity.dir[0]<0:#sword up-left
                        entity.image=entity.images_sword[entity.frame['sword']//3+19]
                        entity.frame['sword']+=1
                    elif entity.dir[0]>0 and entity.dir[1]==0:#sword right and not up or down
                        entity.image=entity.images_sword[entity.frame['sword']//3+1]
                        entity.frame['sword']+=1
                    elif entity.dir[0]<0 and entity.dir[1]==0:#sword left and not up or down
                        entity.image=entity.images_sword[entity.frame['sword']//3+7]
                        entity.frame['sword']+=1
                    elif entity.dir[1]<0:# down
                        entity.image=entity.images_sword[entity.frame['sword']//3+25]
                        entity.frame['sword']+=1

                    #reset frames
                    if entity.frame['sword']==entity.frame_timer['sword']:
                        entity.frame['sword']=1
                        entity.action['sword']=False

                elif not entity.action['sword']:#not sword
                    #jump
                    if entity.action['jump']==True and entity.dir[0]>0:#jump without sword right
                        entity.image=entity.images[entity.frame['jump']//7+21]
                        entity.frame['jump']+=1
                    elif entity.action['jump']==True and entity.dir[0]<0:#jump without sword left
                        entity.image=entity.images[entity.frame['jump']//7+24]
                        entity.frame['jump']+=1
                    #run
                    elif entity.action['run']==True and entity.dir[0]>0:#run right
                        entity.image=entity.images[entity.frame['run']//4+1]
                        entity.frame['run']+=1
                    elif entity.action['run']==True and entity.dir[0]<0:#run left
                        entity.image=entity.images[entity.frame['run']//4+11]
                        entity.frame['run']+=1
                    #stand
                    elif entity.action['stand']==True and entity.dir[0]>0:#stand right
                        entity.image=entity.images[1]
                    elif entity.action['stand']==True and entity.dir[0]<0:#stand left
                        entity.image=entity.images[11]

                    #reset frames
                    if entity.frame['run']==entity.frame_timer['run']:
                        entity.frame['run']=1
                    if entity.frame['jump']==entity.frame_timer['jump']:
                        entity.frame['jump']=1

            else:#if dead
                entity.image=entity.images[entity.frame['death']//4+27]
                entity.frame['death']+=1
                if entity.frame['death']==entity.frame_timer['death']:
                    entity.kill()#remove the sprite after animation
