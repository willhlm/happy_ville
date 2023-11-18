import random, sys

class Camera():
    def __init__(self,game_objects,scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = scroll
        self.scroll = self.true_scroll.copy()
        self.center = [game_objects.map.PLAYER_CENTER[0]-game_objects.player.rect[2]*0.5,game_objects.map.PLAYER_CENTER[1]-game_objects.player.rect[3]*0.5]
        self.original_center = self.center.copy()

    def update(self):
        self.true_scroll[0] += (self.game_objects.player.true_pos[0] - self.true_scroll[0] - self.center[0])*0.1
        self.true_scroll[1] += (self.game_objects.player.true_pos[1] - self.true_scroll[1] - self.center[1])*0.1
        self.scroll = self.true_scroll.copy()

        self.scroll[0] = int(self.scroll[0])
        self.scroll[1] = int(self.scroll[1])

    def set_camera(self, camera):
        self.game_objects.camera = getattr(sys.modules[__name__], camera)(self.game_objects,self.true_scroll)

    def camera_shake(self,amp = 3, duration = 100):
        self.game_objects.camera = Camera_shake(self.game_objects,self.true_scroll,amp,duration)

    def reset_player_center(self):#called when loading a map in maploader
        self.center = self.original_center.copy()
        for stop in self.game_objects.camera_blocks:#apply cameras stopp
            stop.update()
            stop.currentstate.init_pos()

        if self.center[0] == self.original_center[0]: offset_x = 0#if there was no cameras topp
        else: offset_x = self.game_objects.player.rect[2]*0.5#if there was a camera stopp, add this offset
        if self.center[1] == self.original_center[1]: offset_y = 0#if there was no cameras topp
        else: offset_y = self.game_objects.player.rect[3]*0.5#if there was a camera stopp, add this offset

        self.true_scroll = [self.game_objects.player.true_pos[0] - self.center[0] - offset_x, self.game_objects.player.true_pos[1] - self.center[1] - offset_y]#-self.game_objects.player.rect[2]*0.5,-self.game_objects.player.rect[3]*0.5 if there was a camera stopp

class Camera_shake(Camera):
    def __init__(self, game_objects,scroll, amp,duration):
        super().__init__(game_objects,scroll)
        self.amp = amp
        self.duration = duration

    def camera_shake(self,amp=3,duration=100):
        pass

    def update(self):
        super().update()
        self.scroll[0] += random.randint(-self.amp,self.amp)
        self.scroll[1] += random.randint(-self.amp,self.amp)
        self.duration -= self.game_objects.game.dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.set_camera('Camera')

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)
        self.shaking = False

    def update(self):
        super().update()
        self.shakeit()

    def camera_shake(self,amp = 3, duration = 100):#if camera shake is called during a cutscene, set a flag so that it shakes
        self.shaking = True
        self.amp = amp
        self.duration = duration

    def shakeit(self):
        if not self.shaking: return
        self.duration -= self.game_objects.game.dt
        self.scroll[0] += random.randint(-self.amp,self.amp)
        self.scroll[1] += random.randint(-self.amp,self.amp)
        if self.duration < 0:
            self.shaking = False

    def exit_state(self):#called from cutscenes
        self.set_camera('Camera')

class Deer_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects,scroll)

    def update(self):
        self.center[0] -= 5*self.game_objects.game.dt
        self.center[0] = max(200,self.center[0])
        super().update()

class Cultist_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self):
        self.center[0] += 2*self.game_objects.game.dt
        self.center[0] = min(500,self.center[0])
        super().update()

class New_game(Cutscenes):#initialised in New_game state
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)
        self.center[1] = 1000
        self.timer = 5000

    def update(self):
        self.timer -= self.game_objects.game.dt
        if self.timer < 0:
            self.exit_state()
        self.center[1] -= 2*self.game_objects.game.dt
        self.center[1] = max(self.game_objects.map.PLAYER_CENTER[1],self.center[1])
        super().update()

class Title_screen(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self):
        self.center[1] += 2*self.game_objects.game.dt
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.scroll=self.true_scroll.copy()
        self.scroll[1]=int(self.scroll[1])
