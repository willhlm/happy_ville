import pygame

def f_action(sword_enteties,platforms,enemies,screen,scroll):
    for entity in sword_enteties.sprites():#go through the group
        for f_action in entity.f_action:

            if not entity.action['death'] and entity.equipment:#if alive and doing f_action
                if entity.equip=='sword':#if sword is quipped

                    #update sword position based on swing direction
                    entity.equipment.update(entity)
                    pygame.draw.rect(screen, (0,0,255), entity.equipment.rect,2)#draw hitbox

                    #sword collision?
                    collision_plat=pygame.sprite.spritecollideany(entity.equipment,platforms)
                    collision_ene=pygame.sprite.spritecollideany(entity.equipment,enemies,collided)

                    if entity.equipment.lifetime<0:
                        entity.equipment=None#remove the sword

                    #any kind of sword hit
                    if collision_plat or collision_ene and not collision_ene.action['death']:
                        if entity.dir[1]==0:#if horizontal
                            entity.velocity[0]=-entity.dir[0]*10#knock back
                        else:#up or down
                            entity.velocity[1]=entity.dir[1]*10#knock back
                        entity.equipment=None#remove the sword

                    #if hit enemy
                    if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                        collision_ene.health-=entity.dmg
                        collision_ene.action['hurt']=True

                        collision_ene.velocity[0]=entity.dir[0]*10#knock back of enemy

                        entity.equipment=None#remove the sword

                        if collision_ene.health<=0:#if 0 health of enemy
                            collision_ene.action['death']=True
                            collision_ene.action['run']=False

                elif entity.equip=='bow':#if bow is equipeed

                    entity.equipment.update(screen,scroll)

                    #arrow collisions?
                    collision_plat=pygame.sprite.spritecollideany(entity.equipment,platforms)
                    collision_ene=pygame.sprite.spritecollideany(entity.equipment,enemies,collided)

                    pygame.draw.rect(screen, (0,0,255), entity.equipment.hitbox,2)#draw hitbox

                    #remove arrow
                    if collision_plat or collision_ene and not collision_ene.action['death'] or entity.equipment.lifetime<0:
                        entity.equipment=None

                    #if hit enemy
                    if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                        collision_ene.health-=entity.dmg
                        collision_ene.action['hurt']=True

                        entity.equipment=None#remove the sword

                        if collision_ene.health<=0:#if 0 health of enemy
                            collision_ene.action['death']=True
                            collision_ene.action['run']=False

                break# no need to go thourhg other f_actions

def collided(sword,target):
    return sword.rect.colliderect(target.hitbox)
