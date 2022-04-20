import animation
import Read_files
import sys

class Cutscene_Manager():
    def __init__(self,player):
        self.player=player
        self.cutscenes_complete = []
        #test

    def start(self,cutscene,type):
        if type=='file':
            self.current_scene=Cutscene_files(cutscene)
        elif type=='engine':
            self.current_scene=getattr(sys.modules[__name__], cutscene)(self.player)

    def update(self):
        self.current_scene.update()

    def render(self,screen):
        self.current_scene.render(screen)

    def end(self):
        self.cutscenes_complete.append(self.current_scene.name)

class Cutscene_files():
    def __init__(self,cutscene):
        self.name=cutscene
        self.sprites = Read_files.load_sprites('Sprites/Cutscene/'+self.name)
        self.image=self.sprites[0]
        self.finished=False
        self.animation=animation.Cutscene_animation(self)

    def update(self):
        self.animation.update()

    def render(self,screen):
        screen.blit(self.image,(0, 0))

class deer_encounter():
    def __init__(self,player):
        self.player=player

    def update(self):
        pass
        #manimuplate the plater

    def render(self):
        pass
