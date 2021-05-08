import pygame
import Entities

def f_action(sword_enteties,platforms,enemies,screen):
    for entity in sword_enteties.sprites():#go through the group

        for f_action in entity.f_action:

            if entity.action[f_action] and not entity.action['death'] and entity.f_action_cooldown:#if alive and doing f_action

                if f_action=='sword':#if sword is quipped

                    sword=Entities.Sword(entity)#make a sword hitbox

                    #update sword position based on swing direction
                    sword.update(entity)
                    pygame.draw.rect(screen, (0,0,255), sword.rect,2)#draw hitbox

                    #sword collision?
                    collision_plat=pygame.sprite.spritecollideany(sword,platforms)
                    collision_ene=pygame.sprite.spritecollideany(sword,enemies,collided)

                    #any kind of sword hit
                    if collision_plat or collision_ene and not collision_ene.action['death']:
                        if entity.dir[1]==0:#if horizontal
                            entity.velocity[0]=-entity.dir[0]*10#knock back
                        else:#up or down
                            entity.velocity[1]=entity.dir[1]*10#knock back
                        entity.f_action_cooldown=False#a flag to remove hitbox if hit something

                    #if hit enemy
                    if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                        collision_ene.health-=entity.dmg
                        collision_ene.action['hurt']=True

                        collision_ene.velocity[0]=entity.dir[0]*10#knock back of enemy

                        if collision_ene.health<=0:#if 0 health of enemy
                            collision_ene.action['death']=True
                            collision_ene.action['run']=False
                        entity.f_action_cooldown=False#a flag to remove hitbox if hit something

                elif f_action=='bow':#if bow is equipeed
                    pass

                break# no need to go thourhg other f_actions

def collided(sword,target):
    return sword.rect.colliderect(target.hitbox)
