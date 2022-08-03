import animation
import Read_files
import Entities
import pygame
import particles

class Cutscene_engine():
    def __init__(self,parent_class):
        self.parent_class = parent_class

        self.timer=0
        self.pos = [-self.parent_class.game.WINDOW_SIZE[1],self.parent_class.game.WINDOW_SIZE[1]]
        self.const = 0.8#value that determines where the black boxes finish: 0.8 is 20% of screen is covered

    def render(self):
        self.cinematic()

    def cinematic(self):#black box stuff
        self.pos[0]+=1#the upper balck box
        rect1=(0, self.pos[0], self.parent_class.game.WINDOW_SIZE[0], self.parent_class.game.WINDOW_SIZE[1])
        pygame.draw.rect(self.parent_class.game.screen, (0, 0, 0), rect1)

        self.pos[1]-=1#the lower balck box
        rect2=(0, self.pos[1], self.parent_class.game.WINDOW_SIZE[0], self.parent_class.game.WINDOW_SIZE[1])
        pygame.draw.rect(self.parent_class.game.screen, (0, 0, 0), rect2)

        self.pos[0]=min(-self.parent_class.game.WINDOW_SIZE[1]*self.const,self.pos[0])
        self.pos[1]=max(self.parent_class.game.WINDOW_SIZE[1]*self.const,self.pos[1])

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'start':
                self.parent_class.exit_state()
            elif input[-1] == 'a':
                self.press = True

    def exit_state(self):
        self.parent_class.exit_state()

class Deer_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        spawn_pos=(700,130)
        self.entity=Entities.Reindeer(spawn_pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.parent_class.game.game_objects.camera[-1].set_camera('Deer_encounter')

    def update(self):#write how you want the player/group to act
        self.timer+=1
        if self.timer==1:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Walk')#should only enter these states once
        elif self.timer<50:
            self.parent_class.game.game_objects.player.velocity[0]=4
        elif self.timer==50:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Idle')#should only enter these states once
            self.entity.currentstate.enter_state('Walk')
        elif self.timer>50:
            self.parent_class.game.game_objects.player.velocity[0]=0
            self.entity.velocity[0]=5

        if self.timer>200:
            self.exit_state()

    def exit_state(self):
        self.parent_class.game.game_objects.camera[-1].exit_state()
        self.entity.kill()
        super().exit_state()

class Boss_deer_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        pos=(650,140)
        self.entity=Entities.Reindeer(pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.entity.dir[0]=-1
        self.parent_class.game.game_objects.camera[-1].set_camera('Deer_encounter')

    def update(self):#write how you want the player/group to act
        self.entity.velocity[1]=0
        self.timer+=1
        if self.timer==1:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Walk')#should only enter these states once
        elif self.timer<100:
            self.parent_class.game.game_objects.player.velocity[0]=4
        elif self.timer==100:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Idle')#should only enter these states once
            self.entity.currentstate.enter_state('Transform')
            self.parent_class.game.game_objects.player.velocity[0]=-20
            self.parent_class.game.game_objects.camera[-1].camera_shake()#amplitude, duration
        elif self.timer>100:
            pass
            #self.deer.velocity[0]=5

        if self.timer>200:
            self.parent_class.game.game_objects.camera[-1].exit_state()
            self.entity.AImethod=self.entity.aggroAI
            self.exit_state()
            #self.entity.kill()

class Defeated_boss(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        self.image = pygame.image.load("Sprites/UI/Menu/select/inventory1.png").convert_alpha()
        self.press = False
        self.step1 = False
        self.step2 = False
        self.abillity = 'dash'
        self.set_image()
        self.const = 0.5#value that determines where the black boxes finish: 0.8 is 20% of screen is covered

    def set_image(self):
        img=self.parent_class.game.game_objects.player.sprites.sprite_dict['main'][self.abillity][0]
        self.image.blit(img,(50, 0))

    def update(self):
        self.timer+=1
        if self.timer==1:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Idle')#should only enter these states once
        elif self.timer < 75:
            self.parent_class.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.parent_class.game.game_objects.player.velocity[1] = -1#compensates for gravity
            self.step1 = True

        if self.timer > 200:
            self.step2=True

        if self.press:
            self.parent_class.game.game_objects.player.velocity[1] = 2

    def render(self):
        super().render()
        if self.step1:
            particle = particles.General_particle(self.parent_class.game.game_objects.player.rect.center)
            self.parent_class.game.game_objects.cosmetics.add(particle)

            self.parent_class.game.game_objects.cosmetics.draw(self.parent_class.game.game_objects.game.screen)
            self.parent_class.game.game_objects.players.draw(self.parent_class.game.game_objects.game.screen)

        if self.step2 and not self.press:
            self.parent_class.game.game_objects.game.screen.blit(self.image,(100, 50))

        if self.press:
            if self.parent_class.game.game_objects.player.collision_types['bottom']:
                self.parent_class.game.game_objects.cosmetics.empty()
                self.exit_state()

class Death(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        self.parent_class.game.game_objects.camera[-1].set_camera('Death')#make the camera not move
        self.stage = 0

    def update(self):
        self.timer+=1
        if self.stage==0:

            if self.timer>120:
                self.state1()

        elif self.stage==1:
            if self.timer==1:
                pos=(0,0)#
                offset=100#depends on the effect animation
                self.spawneffect=Entities.Spawneffect(pos)
                self.spawneffect.rect.midbottom=self.parent_class.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom+=offset
                self.parent_class.game.game_objects.cosmetics.add(self.spawneffect)

            elif self.spawneffect.finish:#when the cosmetic effetc finishes
                self.parent_class.game.game_objects.player.currentstate.enter_state('Spawn')
                self.exit_state()

    def state1(self):
        self.parent_class.game.game_objects.load_map(self.parent_class.game.game_objects.player.spawn_point[-1]['map'],self.parent_class.game.game_objects.player.spawn_point[-1]['point'])
        self.parent_class.game.game_objects.player.currentstate.enter_state('Invisible')
        self.parent_class.game.game_objects.camera[-1].exit_state()#go to auto camera
        self.stage=1
        self.timer=0

    def exit_state(self):
        if len(self.parent_class.game.game_objects.player.spawn_point)==2:#if the respawn was a bone
            self.parent_class.game.game_objects.player.spawn_point.pop()
        super().exit_state()

    def handle_events(self,input):
        pass

    def cinematic(self):
        pass

class Cultist_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        spawn_pos=(-150,100)
        self.stage = 0
        self.entity1=Entities.Cultist_warrior(spawn_pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.camera[-1].set_camera('Cultist_encounter')
        self.entity1.AImethod=self.entity1.cutsceneAI
        self.parent_class.game.game_objects.enemies.add(self.entity1)

    def update(self):
        self.timer+=1
        if self.stage==0:#encounter Cultist_warrior
            if self.timer==1:
                self.parent_class.game.game_objects.player.currentstate.enter_state('Walk')#should only enter these states once
            elif self.timer<50:
                self.parent_class.game.game_objects.player.velocity[0]=-4
            elif self.timer==50:
                self.parent_class.game.game_objects.player.currentstate.enter_state('Idle')#should only enter these states once
                self.parent_class.game.game_objects.player.velocity[0]=0
            elif self.timer>200:
                self.stage=1
                self.timer=0

        elif self.stage==1:#sapawn cultist_rogue
            if self.timer==1:#enter once
                spawn_pos = self.parent_class.game.game_objects.player.rect.topright
                self.entity2=Entities.Cultist_rogue(spawn_pos, self.parent_class.game.game_objects)
                self.entity2.dir[0]=-1
                self.entity2.currentstate.enter_state('Ambush')
                self.entity2.AImethod=self.entity2.cutsceneAI
                self.parent_class.game.game_objects.enemies.add(self.entity2)
            elif self.timer>100:
                self.exit_state()

    def exit_state(self):
        self.entity1.AImethod=self.entity1.aggroAI
        self.entity2.AImethod=self.entity2.aggroAI
        self.parent_class.game.game_objects.camera[-1].exit_state()
        super().exit_state()
