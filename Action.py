import pygame

def actions(projectiles,sword_enteties,platforms,enemies,screen):
    for entity in sword_enteties.sprites():#go through the group
        projectiles=entity.attack_action(projectiles)
        for projectile in projectiles.sprites():#go through the group

            #equipment collision?
            collision_plat=pygame.sprite.spritecollideany(projectile,platforms)
            collision_ene=pygame.sprite.spritecollideany(projectile,enemies,collided)

            pygame.draw.rect(screen, (0,0,255), projectile.rect,2)#draw hitbox


            #if hit enemy
            if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                collision_ene.health-=projectile.dmg
                collision_ene.action['hurt']=True

                if collision_ene.health<=0:#if 0 health of enemy
                    collision_ene.action['death']=True
                    collision_ene.action['run']=False

                if projectile=='sword':#knockback if sword is quipped
                    collision_ene.velocity[0]=entity.dir[0]*10#knock back of enemy

                projectiles.remove(projectile)

            #hit platform
            elif collision_plat:
                if projectile.type=='sword':#knockback if sword is quipped
                    if entity.dir[1]==0:#if horizontal
                        entity.velocity[0]=-entity.dir[0]*10#knock back
                    else:#up or down
                        entity.velocity[1]=entity.dir[1]*10#knock back

                projectiles.remove(projectile)

            if projectile.lifetime<0:
                projectiles.remove(projectile)

        return projectiles




def f_action(sword_enteties,platforms,enemies,screen,scroll):
    for entity in sword_enteties.sprites():#go through the group

        if not entity.action['death'] and entity.equipment:#if alive and has something equipped

            #update sword position based on swing direction
            entity.equipment.update(entity,screen,scroll)
            pygame.draw.rect(screen, (0,0,255), entity.equipment.rect,2)#draw hitbox

            #remove the equipment if it has expiered
            if entity.equipment.lifetime<0:
                entity.equipment=None
                break

            #equipment collision?
            collision_plat=pygame.sprite.spritecollideany(entity.equipment,platforms)
            collision_ene=pygame.sprite.spritecollideany(entity.equipment,enemies,collided)

            #if hit enemy
            if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                collision_ene.health-=entity.equipment.dmg
                collision_ene.action['hurt']=True

                if collision_ene.health<=0:#if 0 health of enemy
                    collision_ene.action['death']=True
                    collision_ene.action['run']=False

                if entity.equip=='sword':#knockback if sword is quipped
                    collision_ene.velocity[0]=entity.dir[0]*10#knock back of enemy

                entity.equipment=None#remove the equipment if hit enemy

            #hit platform
            elif collision_plat:
                if entity.equip=='sword':
                    if entity.dir[1]==0:#if horizontal
                        entity.velocity[0]=-entity.dir[0]*10#knock back
                    else:#up or down
                        entity.velocity[1]=entity.dir[1]*10#knock back

                entity.equipment=None#remove the equipment if hit platform


def collided(sword,target):
    return sword.rect.colliderect(target.hitbox)
