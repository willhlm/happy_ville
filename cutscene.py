import animation
import Read_files
import Entities

class Cutscene_files():
    def __init__(self,cutscene):
        self.name=cutscene
        self.sprites = Read_files.load_sprites('cutscene/'+self.name)
        self.image=self.sprites[0]
        self.finished=False
        self.animation=animation.Cutscene_animation(self)

    def update(self):
        self.animation.update()

    def render(self,screen):
        screen.blit(self.image,(0, 0))

class Cutscene_engine():
    def __init__(self,objects):
        self.name=type(self).__name__
        self.finished=False
        self.timer=0

        self.game_objects=objects
        self.player = objects.player

class Deer_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        pos=(700,130)
        self.entity=Entities.Reindeer(pos, objects)
        objects.enemies.add(self.entity)

        self.game_objects.camera[-1].set_camera('Deer_encounter')

    def update(self):#write how you want the player/group to act
        self.timer+=1
        if self.timer==1:
            self.player.currentstate.change_state('Walk')#should only enter these states once
        elif self.timer<50:
            self.player.velocity[0]=4
        elif self.timer==50:
            self.player.currentstate.change_state('Idle')#should only enter these states once
            self.entity.currentstate.change_state('Walk')
        elif self.timer>50:
            self.player.velocity[0]=0
            self.entity.velocity[0]=5

        if self.timer>100:
            self.finished=True
            self.game_objects.camera[-1].exit_state()
            self.entity.kill()

class Boss_deer_encounter(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)
        pos=(650,140)
        self.entity=Entities.Reindeer(pos, objects)
        objects.enemies.add(self.entity)
        self.entity.dir[0]=-1

        self.game_objects.camera[-1].set_camera('Deer_encounter')

    def update(self):#write how you want the player/group to act
        self.entity.velocity[1]=0
        self.timer+=1
        if self.timer==1:
            self.player.currentstate.change_state('Walk')#should only enter these states once
        elif self.timer<100:
            self.player.velocity[0]=4
        elif self.timer==100:
            self.player.currentstate.change_state('Idle')#should only enter these states once
            self.entity.currentstate.change_state('Transform')
            self.player.velocity[0]=-20
            self.game_objects.camera[-1].exit_state()
            self.game_objects.camera[-1].set_camera('Camera_shake')
        elif self.timer>100:
            pass
            #self.deer.velocity[0]=5

        if self.timer>200:
            self.game_objects.camera[-1].exit_state()
            self.finished=True
            #self.entity.kill()

class Defeated_boss(Cutscene_engine):
    def __init__(self,objects):
        super().__init__(objects)

    def update(self):
        self.timer+=1
        if self.timer==1:
            self.player.currentstate.change_state('Idle')#should only enter these states once
        elif self.timer<50:
            self.player.velocity[1]=2
        elif self.timer>50:
            self.player.velocity[1]=0

        if self.timer >100:
            self.player.velocity[1]=-2

        if self.timer>200:
            self.finished=True
