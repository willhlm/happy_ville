import pygame
import Entities

def swing_sword(sword_enteties,platforms,enemies,screen):
    for entity in sword_enteties.sprites():#go through the group
        if entity.action['sword'] and not entity.action['death']:#if alive swinning sword
            sword=Entities.Items(entity)#make a sword hitbox

            #update sword position based on swing direction
            sword.update(entity)
            pygame.draw.rect(screen, (0,0,255), sword.rect,2)#draw hitbox

            #sword collision?
            collision_plat=pygame.sprite.spritecollideany(sword,platforms)
            collision_ene=pygame.sprite.spritecollideany(sword,enemies,collided)

            #if sword hit
            if collision_plat or collision_ene and not collision_ene.action['death']:#any kind of sword hit
                if entity.dir[1]>0:#up
                    entity.movement[1]=5#knock back
                elif entity.dir[1]<0:#down
                    entity.movement[1]=-10#knock back
                elif entity.dir[0]>0:#right
                    entity.velocity[0]=-10#knock back
                elif entity.dir[0]<0:#left
                    entity.velocity[0]=10#knock back
            if collision_ene and not collision_ene.action['death'] and not collision_ene.action['dmg']:#if hit alive enemy
                collision_ene.health-=entity.dmg
                collision_ene.action['dmg']=True
                if entity.dir[0]>0:#right
                    collision_ene.velocity[0]=10#knock back
                elif entity.dir[0]<0:#left
                    collision_ene.velocity[0]=-10#knock back
                if collision_ene.health<=0:#if 0 health
                    collision_ene.action['death']=True
                    collision_ene.action['run']=False

def collided(sword,target):
    return sword.rect.colliderect(target.hitbox)
