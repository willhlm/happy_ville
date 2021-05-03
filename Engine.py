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
            if collision_types['top']:#knock back when hit head
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
    def set_img(enteties,sprite_img):
        
        for entity in enteties.sprites():#go through the group



            #need to order according to priority

            if not entity.action['death']:#if not dead
                if entity.action['dmg']:#if took dmg
                    entity.image=sprite_img.hurt[entity.frame//10]
                    entity.frame+=1

                    #reset frames
                    if entity.frame==entity.frame_timer['dmg']:
                        entity.frame=1
                        entity.action['dmg']=False

                elif entity.action['sword']:#sword
                    if entity.dir[1]>0 and entity.dir[0]>0:#sword up-right
                        entity.image=sprite_img.attack_up_right[entity.frame//3]
                        entity.frame+=1
                    elif entity.dir[1]>0 and entity.dir[0]<0:#sword up-left
                        entity.image=sprite_img.attack_up_left[entity.frame//3]
                        entity.frame+=1
                    elif entity.dir[0]>0 and entity.dir[1]==0:#sword right and not up or down
                        entity.image=sprite_img.attack_right[entity.frame//3]
                        entity.frame+=1
                    elif entity.dir[0]<0 and entity.dir[1]==0:#sword left and not up or down
                        entity.image=sprite_img.attack_left[entity.frame//3]
                        entity.frame+=1
                    elif entity.dir[1]<0 and entity.dir[0]>0:# down
                        entity.image=sprite_img.attack_down_right[entity.frame//3]
                        entity.frame+=1
                    elif entity.dir[1]<0 and entity.dir[0]<0:# down
                        entity.image=sprite_img.attack_down_left[entity.frame//3]
                        entity.frame+=1

                    #reset frames
                    if entity.frame==entity.frame_timer['sword']:
                        entity.frame=1
                        entity.action['sword']=False

                elif not entity.action['sword']:#not sword
                    #jump
                    if entity.action['jump']==True and entity.dir[0]>0:#jump without sword right
                        entity.image=sprite_img.jump_right[entity.frame//7]
                        entity.frame+=1
                    elif entity.action['jump']==True and entity.dir[0]<0:#jump without sword left
                        entity.image=sprite_img.jump_left[entity.frame//7]
                        entity.frame+=1
                    #run
                    elif entity.action['run']==True and entity.dir[0]>0:#run right
                        entity.image=sprite_img.run_right[entity.frame//4]
                        entity.frame+=1
                    elif entity.action['run']==True and entity.dir[0]<0:#run left
                        entity.image=sprite_img.run_left[entity.frame//4]
                        entity.frame+=1
                    #stand
                    elif entity.action['stand']==True and entity.dir[0]>0:#stand right
                        entity.image=sprite_img.run_right[0]
                    elif entity.action['stand']==True and entity.dir[0]<0:#stand left
                        entity.image=sprite_img.run_left[0]

                    #reset frames
                    if entity.frame==entity.frame_timer['run']:
                        entity.frame=1
                    if entity.frame == entity.frame_timer['jump']:
                        entity.frame = 1

            else:#if dead
                entity.image=sprite_img.death[entity.frame//4]
                entity.frame+=1
                if entity.frame==entity.frame_timer['death']:
                    entity.kill()#remove the sprite after animation
