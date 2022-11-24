import random, sys

class Camera():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.true_scroll = [0,0]
        self.scroll = [0,0]
        self.center = list(game_objects.map.PLAYER_CENTER)
        self.original_center = self.center.copy()
        self.shake = [0,0]

    def update(self):
        self.check_camera_border_new()
        self.true_scroll[0] += (self.game_objects.player.rect.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.true_scroll[1] += (self.game_objects.player.rect.center[1]-8*self.true_scroll[1]-self.center[1])/15
        self.scroll = self.true_scroll.copy()
        self.scroll[0] = int(self.scroll[0])+self.shake[0]
        self.scroll[1] = int(self.scroll[1])+self.shake[1]

    def set_camera(self, camera):
        new_camera = getattr(sys.modules[__name__], camera)(self.game_objects)
        self.game_objects.camera = new_camera

    def camera_shake(self,amp=3,duration=100):
        self.game_objects.camera = Camera_shake(self.game_objects,amp,duration)

    def reset_player_center(self):
        self.center = self.original_center.copy()

    def check_camera_border_new(self):
        xflag = True
        yflag = True
        for stop in self.game_objects.camera_blocks:
            if stop.dir == 'right':
                if (stop.rect.bottom > 0) and (stop.rect.top < self.game_objects.game.WINDOW_SIZE[1]):
                    if -self.game_objects.game.WINDOW_SIZE[0] < (stop.rect.left - self.game_objects.player.hitbox.centerx) < self.game_objects.game.WINDOW_SIZE[0]/2:
                        self.center[0] = self.game_objects.game.WINDOW_SIZE[0] - (stop.rect.left - self.game_objects.player.hitbox.centerx)
                        xflag = False
                    else:
                        self.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]
                else:
                    self.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]

            if stop.dir == 'left' and xflag:
                if (stop.rect.bottom > 0) and (stop.rect.top < self.game_objects.game.WINDOW_SIZE[1]):
                    if -self.game_objects.game.WINDOW_SIZE[0] < (self.game_objects.player.hitbox.centerx - stop.rect.right) < self.game_objects.game.WINDOW_SIZE[0]/2:
                        self.center[0] =  self.game_objects.player.hitbox.centerx - stop.rect.right
                    else:
                        self.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]
                else:
                    self.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]

            if stop.dir == 'bottom':
                if (stop.rect.left <= self.game_objects.game.WINDOW_SIZE[0]) and (stop.rect.right > 0):
                    if -self.game_objects.game.WINDOW_SIZE[1] < (stop.rect.top - self.game_objects.player.hitbox.centery) < self.game_objects.game.WINDOW_SIZE[1]/2:
                        self.center[1] = self.game_objects.game.WINDOW_SIZE[1] - (stop.rect.top - self.game_objects.player.hitbox.centery)
                        yflag = False
                    else:
                        self.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]
                else:
                    self.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]

            if stop.dir == 'top' and yflag:
                if (stop.rect.left <= self.game_objects.game.WINDOW_SIZE[0]) and (stop.rect.right > 0):
                    if -self.game_objects.game.WINDOW_SIZE[1] < (self.game_objects.player.hitbox.centery - stop.rect.bottom) < self.game_objects.game.WINDOW_SIZE[1]/2:
                        self.center[1] = self.game_objects.player.hitbox.centery - stop.rect.bottom
                    else:
                        self.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]
                else:
                    self.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]

class Camera_shake(Camera):
    def __init__(self, game_objects,amp,duration):
        super().__init__(game_objects)
        self.amp = amp
        self.duration = duration

    def camera_shake(self,amp=3,duration=100):
        pass

    def update(self):
        self.shake[0] = random.randint(-self.amp,self.amp)
        self.shake[1] = random.randint(-self.amp,self.amp)
        super().update()
        self.duration -= 1
        self.exit_state()

    def exit_state(self):#go back to the cameera we came from
        if self.duration < 0:
            self.set_camera('Camera')

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.shaking = False

    def update(self):
        super().update()
        self.shakeit()

    def camera_shake(self,amp = 3, duration = 100):
        self.shaking = True
        self.amp = amp
        self.duration = duration

    def shakeit(self):
        if self.shaking:
            self.duration -= 1
            self.shake[0] = random.randint(-self.amp,self.amp)
            self.shake[1] = random.randint(-self.amp,self.amp)
            if self.duration < 0:
                self.shaking = False

    def exit_state(self):
        self.set_camera('Camera')

class Deer_encounter(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[0] -= 5
        self.center[0] = max(200,self.center[0])
        super().update()

class Cultist_encounter(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[0] += 2
        self.center[0] = min(500,self.center[0])
        super().update()

class New_game(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.center[1] = 1000

    def update(self):
        self.center[1] -= 2
        self.center[1] = max(self.game_objects.map.PLAYER_CENTER[1],self.center[1])
        super().update()

class Title_screen(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[1] += 2
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.check_camera_border_new()
        self.scroll=self.true_scroll.copy()
        self.scroll[1]=int(self.scroll[1])+self.shake[1]
