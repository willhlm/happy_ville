import Read_files
import Entities
import pygame
import particles
import animation
import states
import random
import constants as C

class Cutscene_file():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self,parent_class):
        self.parent_class = parent_class
        self.game_objects = parent_class.game.game_objects
        self.animation=animation.Simple_animation(self)
        self.sprites = Read_files.load_sprites('cutscene/'+type(self).__name__.lower())
        self.image=self.sprites[0]

    def update(self):
        self.animation.update()

    def render(self):
        self.parent_class.game.screen.blit(self.image,(0, 0))

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        pass

class Rhoutta_encounter(Cutscene_file):#play the first cutscene encountering rhoutta
    def __init__(self,objects):
        super().__init__(objects)
        self.parent_class.game.game_objects.load_map('wakeup_forest_1',fade = False)#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.parent_class.exit_state()
        new_state=states.Cutscenes(self.parent_class.game,'Title_screen')
        new_state.enter_state()

class Cutscene_engine():#cut scenens that is based on game engien
    def __init__(self,parent_class):
        self.parent_class = parent_class

        self.timer = 0
        self.pos = [-self.parent_class.game.WINDOW_SIZE[1],self.parent_class.game.WINDOW_SIZE[1]]
        self.const = 0.8#value that determines where the black boxes finish: 0.8 is 20% of screen is covered

    def render(self):
        self.cinematic()

    def cinematic(self):#black box stuff
        self.pos[0]+=self.parent_class.game.dt#the upper balck box
        rect1=(0, int(self.pos[0]), self.parent_class.game.WINDOW_SIZE[0], self.parent_class.game.WINDOW_SIZE[1])
        pygame.draw.rect(self.parent_class.game.screen, (0, 0, 0), rect1)

        self.pos[1]-=self.parent_class.game.dt#the lower balck box
        rect2=(0, int(self.pos[1]), self.parent_class.game.WINDOW_SIZE[0], self.parent_class.game.WINDOW_SIZE[1])
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

class New_game(Cutscene_engine):#first screen to be played when starying a new game
    def __init__(self,objects):
        super().__init__(objects)
        self.parent_class.game.game_objects.camera.set_camera('New_game')

    def cinematic(self):
        pass

    def update(self):
        self.timer+=self.parent_class.game.dt
        if self.timer>500:
            self.exit_state()

    def exit_state(self):
        self.parent_class.game.game_objects.camera.exit_state()
        super().exit_state()

class Title_screen(Cutscene_engine):#screen played after waking up from boss dream
    def __init__(self,objects):
        super().__init__(objects)
        self.title_name = self.parent_class.game.game_objects.font.render(text = 'Happy Ville')
        self.text1 = self.parent_class.game.game_objects.font.render(text = 'A game by Hjortron games')
        C.acceleration = [0.3,0.51]#restrict the speed
        self.stage = 0
        self.press = False

    def update(self):
        self.timer+=self.parent_class.game.dt

    def render(self):
        if self.stage == 0:#running slowly and blit title, Hjortron games etc.
            if self.timer>400:
                self.parent_class.game.screen.blit(self.title_name,(190,150))

            if self.timer>1000:
                self.parent_class.game.screen.blit(self.text1,(190,170))

            if self.timer >1200:
                self.stage += 1
                self.init_stage1()

        elif self.stage == 1:#camera moves up and aila runs away
            if self.timer == 1300:
                self.parent_class.game.game_objects.player.acceleration[0] = 0
                self.parent_class.game.game_objects.player.enter_idle()

            if self.timer > 1500:
                self.parent_class.game.screen.blit(self.title_name,(190,150))


            if self.timer > 1550:
                if self.press:
                    self.stage += 1
                    self.parent_class.game.game_objects.camera.exit_state()
                    self.parent_class.game.game_objects.load_map('village_1')
                    self.timer = 0
                    self.pos = [-self.parent_class.game.WINDOW_SIZE[1],self.parent_class.game.WINDOW_SIZE[1]]

        elif self.stage == 2:#cutscenen in village
            self.cinematic()
            if self.timer == 200:#make him movev to aila
                spawn_pos=(0,130)

                self.entity = Entities.Aslat(spawn_pos, self.parent_class.game.game_objects)

                self.parent_class.game.game_objects.npcs.add(self.entity)
                self.entity.currentstate.enter_state('Walk')
            elif self.timer == 320:#make it stay still
                self.entity.currentstate.enter_state('Idle')
            elif self.timer == 400:#start conversation
                self.entity.interact()
            elif self.timer > 410:
                self.exit_state()

    def handle_events(self,input):
        super().handle_events(input)
        if self.stage == 0:
            #can only go left
            if input[2][0] > 0: return
            self.parent_class.game.game_objects.player.currentstate.handle_movement(input)

    def init_stage1(self):
        C.acceleration = [1,0.51]#reset to normal movement
        input = [0,0,[-1,0],0]
        self.parent_class.game.game_objects.player.currentstate.handle_movement(input)
        self.parent_class.game.game_objects.camera.set_camera('Title_screen')

class Deer_encounter(Cutscene_engine):#first deer encounter in light forest by waterfall
    def __init__(self,objects):
        super().__init__(objects)
        spawn_pos=(700,130)
        self.entity=Entities.Reindeer(spawn_pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.parent_class.game.game_objects.camera.set_camera('Deer_encounter')
        self.parent_class.game.game_objects.player.currentstate.enter_state('Walk')#should only enter these states once

    def update(self):#write how you want the player/group to act
        self.timer+=self.parent_class.game.dt
        if self.timer<50:
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
        self.parent_class.game.game_objects.camera.exit_state()
        self.entity.kill()
        super().exit_state()

class Boss_deer_encounter(Cutscene_engine):#boss fight cutscene
    def __init__(self,objects):
        super().__init__(objects)
        pos = (900,100)
        self.entity = Entities.Reindeer(pos, self.parent_class.game.game_objects)#make the boss
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.entity.dir[0]=-1
        self.parent_class.game.game_objects.camera.set_camera('Deer_encounter')
        self.entity.AI.deactivate()
        self.stage = 0
        self.parent_class.game.game_objects.player.currentstate.enter_state('Walk_main')

    def update(self):#write how you want the player/group to act
        self.timer+=self.parent_class.game.dt
        if self.stage == 0:
            self.parent_class.game.game_objects.player.velocity[0]  = 4

            if self.timer >120:
                self.stage=1
                self.parent_class.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.parent_class.game.game_objects.player.acceleration[0]=0

        elif self.stage==1:
            if self.timer>200:
                self.entity.currentstate.enter_state('Transform')
                self.parent_class.game.game_objects.player.velocity[0] = -20
                self.parent_class.game.game_objects.camera.camera_shake(amp=3,duration=100)#amplitude, duration
                self.stage=2

        elif self.stage==2:
            if self.timer > 400:
                self.parent_class.game.game_objects.camera.exit_state()#exsiting deer encounter camera
                self.entity.AI.activate()
                self.exit_state()

class Defeated_boss(Cutscene_engine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self.step1 = False
        self.const = 0.5#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.parent_class.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once

    def update(self):
        self.timer+=self.parent_class.game.dt
        if self.timer < 75:
            self.parent_class.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.parent_class.game.game_objects.player.velocity[1] = -1#compensates for gravity, levitates
            self.step1 = True

        if self.timer > 250:
            self.parent_class.game.game_objects.player.velocity[1] = 2#go down again
            if self.parent_class.game.game_objects.player.collision_types['bottom']:
                self.exit_state()

    def render(self):
        super().render()
        if self.step1:
            particle = getattr(particles, 'Spark')(self.parent_class.game.game_objects.player.rect.center,self.parent_class.game.game_objects,distance = 400, lifetime = 60, vel = [7,13], dir = 'isotropic', scale = 1, colour = [255,255,255,255])
            self.parent_class.game.game_objects.cosmetics.add(particle)

            self.parent_class.game.game_objects.cosmetics.draw(self.parent_class.game.game_objects.game.screen)
            self.parent_class.game.game_objects.players.draw(self.parent_class.game.game_objects.game.screen)

class Death(Cutscene_engine):#when aila dies
    def __init__(self,objects):
        super().__init__(objects)
        self.stage = 0

    def update(self):
        self.timer += self.parent_class.game.dt
        if self.stage == 0:

            if self.timer > 120:
                self.state1()

        elif self.stage == 1:
                #spawn effect
                pos=(0,0)#
                offset=100#depends on the effect animation
                self.spawneffect = Entities.Spawneffect(pos,self.parent_class.game.game_objects)
                self.spawneffect.rect.midbottom=self.parent_class.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom += offset
                self.parent_class.game.game_objects.cosmetics.add(self.spawneffect)
                self.stage = 2

        elif self.stage == 2:
            if self.spawneffect.finish:#when the cosmetic effetc finishes
                self.parent_class.game.game_objects.player.currentstate.enter_state('Spawn_main')
                self.exit_state()

    def state1(self):
        self.parent_class.game.game_objects.load_map(self.parent_class.game.game_objects.player.spawn_point[-1]['map'],self.parent_class.game.game_objects.player.spawn_point[-1]['point'])
        self.parent_class.game.game_objects.player.currentstate.enter_state('Invisible_main')
        self.stage = 1
        self.timer = 0

    def exit_state(self):
        if len(self.parent_class.game.game_objects.player.spawn_point) == 2:#if the respawn was a bone
            self.parent_class.game.game_objects.player.spawn_point.pop()
        super().exit_state()

    def handle_events(self,input):
        pass

    def cinematic(self):
        pass

class Cultist_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        spawn_pos = (-150,100)
        self.stage = 0
        self.entity1=Entities.Cultist_warrior(spawn_pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.camera.set_camera('Cultist_encounter')
        self.entity1.AI.enter_AI('Nothing')
        self.parent_class.game.game_objects.enemies.add(self.entity1)
        self.parent_class.game.game_objects.player.currentstate.enter_state('Walk_main')#should only enter these states once

    def update(self):
        self.timer+=self.parent_class.game.dt

        if self.stage==0:#encounter Cultist_warrior
            if self.timer<50:
                self.parent_class.game.game_objects.player.velocity[0]=-4
                self.parent_class.game.game_objects.player.acceleration[0]=1

            elif self.timer > 50:
                self.parent_class.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.parent_class.game.game_objects.player.velocity[0]=0
                self.parent_class.game.game_objects.player.acceleration[0]=0

                self.stage = 1

        elif self.stage == 1:
            if self.timer>200:
                spawn_pos = self.parent_class.game.game_objects.player.rect.topright
                self.entity2=Entities.Cultist_rogue(spawn_pos, self.parent_class.game.game_objects)
                self.entity2.dir[0]=-1
                self.entity2.currentstate.enter_state('Ambush_pre')
                self.entity2.AI.enter_AI('Nothing')
                self.parent_class.game.game_objects.enemies.add(self.entity2)

                self.stage=2
                self.timer=0

        elif self.stage==2:#sapawn cultist_rogue
            if self.timer>100:
                self.exit_state()

    def exit_state(self):
        self.entity1.AI.enter_AI('Chase')
        self.entity2.AI.enter_AI('Chase')
        self.parent_class.game.game_objects.camera.exit_state()
        super().exit_state()
