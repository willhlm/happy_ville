import pygame

def actions(projectiles,projectile_enteties,platforms,enemies,screen,loot):
    for entity in projectile_enteties.sprites():#go through the group
        projectiles=entity.attack_action(projectiles)

        for projectile in projectiles.sprites():#go through the group

            #projectile collision?
            collision_plat = pygame.sprite.spritecollideany(projectile,platforms,collided)
            collision_ene = pygame.sprite.spritecollideany(projectile,enemies,collided)

            pygame.draw.rect(screen, (0,0,255), projectile.hitbox,2)#draw hitbox

            #if hit enemy
            if collision_ene and not collision_ene.action['death'] and not collision_ene.action['hurt']:
                collision_ene.health-=projectile.dmg
                collision_ene.action['hurt']=True

                if collision_ene.health<=0:#if 0 health of enemy
                    collision_ene.action['death']=True
                    collision_ene.action['run']=False
                    loot=collision_ene.loots(loot)

                if projectile.type=='sword':#knockback if sword is quipped
                    collision_ene.velocity[0]=entity.dir[0]*10#knock back of enemy
                    projectiles.remove(projectile)

                    if entity.dir[1]!=0:##up or down
                        entity.velocity[1]=entity.dir[1]*10#nail jump

                elif projectile.type=='bow':
                    projectile.velocity=[0,0]

            #hit platform
            elif collision_plat:
                if projectile.type=='sword':#knockback if sword is quipped
                    if entity.dir[1]==0:#if horizontal
                        entity.velocity[0]=-entity.dir[0]*10#knock back
                    else:#up or down
                        entity.velocity[1]=entity.dir[1]*10#knock back
                    projectiles.remove(projectile)
                elif projectile.type=='bow':
                    projectile.velocity=[0,0]

            if projectile.lifetime<0:
                projectiles.remove(projectile)

    return projectiles, loot

def collided(projectile,target):
    return projectile.hitbox.colliderect(target.hitbox)
