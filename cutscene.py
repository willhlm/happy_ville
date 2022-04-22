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

class Cutscene_engine():
    def __init__(self,objects,trigger):
        self.name=type(self).__name__
        self.finished=False
        self.timer=0

        self.player = objects.player
        self.camera = objects.map

        if hasattr(trigger, 'entity'):#if entity should be made
            pos=(0,0)
            self.entity=getattr(Entities, trigger.entity)(pos, objects.eprojectiles, objects.loot,objects.enemies,objects.entity_pause)
            objects.enemies.add(self.entity)

class Deer_encounter(Cutscene_engine):
    def __init__(self,objects,trigger):
        super().__init__(objects,trigger)
        pos=(700,130)
        self.entity.set_pos(pos)
        self.camera.set_camera(5)

    def update(self):#write how you want the player/group to act
        #self.entity.velocity[1]=0
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
            self.entity.kill()

class Boss_deer_encounter(Cutscene_engine):
    def __init__(self,objects,trigger):
        super().__init__(objects,trigger)
        pos=(650,130)
        self.entity.set_pos(pos)
        self.entity.dir[0]=-1
        self.camera.set_camera(5)

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
            self.camera.set_camera(4)
        elif self.timer>100:
            pass
            #self.deer.velocity[0]=5

        if self.timer>200:
            self.finished=True
            #self.entity.kill()
