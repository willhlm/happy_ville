import pygame

class Items():
    def __init__(self):
        #super().__init__()
        self.hit=False

class Sword(Items):
    def __init__(self):
        super().__init__()
        self.movement=[0,0]

    def update(self,entity):
        if entity.ac_dir[0]>0 and entity.ac_dir[1]==0:#right
            self.rect=pygame.Rect(entity.hitbox.midright[0],entity.hitbox.midright[1]-20,40,40)
        elif entity.ac_dir[0]<0 and entity.ac_dir[1]==0:#left
            self.rect=pygame.Rect(entity.hitbox.midleft[0]-40,entity.hitbox.midleft[1]-20,40,40)
        elif entity.ac_dir[1]>0:#up
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]-20,20,20)
        elif entity.ac_dir[1]<0:#down
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]+50,20,20)

def f_action(sword_enteties,platforms,enemies,screen):
    for entity in sword_enteties.sprites():#go through the group
        for f_action in entity.f_action:

            if entity.action[f_action] and not entity.action['death'] and entity.f_action_cooldown:#if alive and doing f_action
                if f_action=='sword':#if sword is quipped

                    sword=Sword()#make a sword hitbox

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

                        entity.f_action_cooldown=False#a flag to remove hitbox if hit something

                        if collision_ene.health<=0:#if 0 health of enemy
                            collision_ene.action['death']=True
                            collision_ene.action['run']=False

                elif f_action=='bow':#if bow is equipeed
                    pass

                break# no need to go thourhg other f_actions

def collided(sword,target):
    return sword.rect.colliderect(target.hitbox)
