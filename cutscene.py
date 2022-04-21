import animation
import Read_files
import Entities

class Cutscene_Manager():
    def __init__(self):
        self.cutscenes_complete = []

    def start(self,scene):
        self.cutscenes_complete.append(scene)

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

class deer_encounter():
    def __init__(self,player,group):
        self.name=type(self).__name__
        self.player=player
        self.finished=False
        self.timer=0

        pos=(650,170)
        self.deer = Entities.Cutscene_reindeer(pos)
        group.add(self.deer)

    def update(self):#write how you want the plater want to act
        self.timer+=1
        if self.timer==1:
            self.player.currentstate.change_state('Walk')#should only enter these states once
        elif self.timer<50:
            self.player.velocity[0]=4
            self.deer.currentstate.change_state('Idle')
        elif self.timer==50:
            self.player.currentstate.change_state('Idle')#should only enter these states once
            self.deer.currentstate.change_state('Walk')
            #self.deer.dir[0]=-self.deer.dir[0]
        elif self.timer>50:
            self.player.velocity[0]=0
            self.deer.velocity[0]=5

        if self.timer>100:
            self.finished=True
            self.deer.kill()

    def render(self):
        pass
