import pygame

def actions(projectiles,projectile_enteties,platforms,enemies,screen,loot):
    for entity in projectile_enteties.sprites():#go through the group
        projectiles=entity.attack_action(projectiles)

        for projectile in projectiles.sprites():#go through the group

            #projectile collision?
            collision_plat = pygame.sprite.spritecollideany(projectile,platforms,collided)
            collision_enemy = pygame.sprite.spritecollideany(projectile,enemies,collided)

            pygame.draw.rect(screen, (0,0,255), projectile.hitbox,2)#draw hitbox

            #if hit enemy
            if collision_enemy and not collision_enemy.action['death'] and not collision_enemy.action['hurt']:

                entity.shake=collision_enemy.shake#screen shake

                collision_enemy.health-=projectile.dmg
                collision_enemy.action['hurt']=True

                if collision_enemy.health<=0:#if 0 health of enemy
                    collision_enemy.action['death']=True
                    collision_enemy.action['run']=False
                    loot=collision_enemy.loots(loot)

                if projectile.type=='sword':#knockback if sword is quipped
                    #collision_enemy.velocity[0]=entity.dir[0]*10#knock back of enemy
                    projectiles.remove(projectile)
                    entity.velocity[1]=entity.dir[1]*10#nail jump

                elif projectile.type=='bow':
                    projectile.velocity=[0,0]

            #hit platform
            elif collision_plat:
                if projectile.type=='sword':#knockback if sword is quipped
                    #entity.velocity[0]=entity.dir[0]*10*(abs(entity.dir[1])-1)#knock back horizontally
                    entity.velocity[1]=entity.dir[1]*10#nail jump
                    projectiles.remove(projectile)
                elif projectile.type=='bow':
                    projectile.velocity=[0,0]

            if projectile.lifetime<0:
                projectiles.remove(projectile)

    return projectiles, loot

def collided(projectile,target):
    return projectile.hitbox.colliderect(target.hitbox)
