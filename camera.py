import random, sys

class Camera():
    def __init__(self,game_objects,true_scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = true_scroll
        self.scroll = true_scroll
        self.center = list(game_objects.map.PLAYER_CENTER)
        self.shake = [0,0]

    def update(self):
        self.check_camera_border()
        self.scroll=self.true_scroll.copy()
        self.scroll[0] = int(self.scroll[0])+self.shake[0]
        self.scroll[1] = int(self.scroll[1])+self.shake[1]

    def set_camera(self, camera):
        new_camera = getattr(sys.modules[__name__], camera)(self.game_objects, self.true_scroll)
        self.game_objects.camera = new_camera

    def camera_shake(self,amp=3,duration=100):
        self.game_objects.camera = Camera_shake(self,amp,duration)

    def handle_input(self,xflag,yflag):
        pass

    def check_camera_border(self):
        xflag, yflag = False, False
        for stop in self.game_objects.camera_blocks:
            if stop.dir == 'right':
                if (self.game_objects.player.hitbox.centery - stop.rect.bottom < self.center[1]) and (stop.rect.top - self.game_objects.player.hitbox.centery < self.game_objects.game.WINDOW_SIZE[1] - self.center[1]):
                    #if -self.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.player.hitbox.centerx) < self.player_center[0]:
                    if -self.game_objects.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.center[0]) < self.center[0] and self.game_objects.player.hitbox.centerx >= self.center[0]:
                        xflag = True
            elif stop.dir == 'left':
                if stop.rect.right >= 0 and self.game_objects.player.hitbox.centerx < self.center[0]:
                    xflag = True
            elif stop.dir == 'bottom':
                if (stop.rect.left - self.game_objects.player.hitbox.centerx < self.center[0]) and (self.game_objects.player.hitbox.centerx - stop.rect.right < self.center[0]):
                    if (-self.game_objects.game.WINDOW_SIZE[1] < (stop.rect.centery - self.game_objects.player.hitbox.centery) < (self.game_objects.game.WINDOW_SIZE[1] - self.center[1])):
                        yflag = True
            elif stop.dir == 'top':
                if (0 < stop.rect.left - self.game_objects.player.hitbox.centerx < self.center[0]) or (0 < self.game_objects.player.hitbox.centerx - stop.rect.right < self.center[0]):
                    if self.game_objects.player.hitbox.centery - stop.rect.centery < 180 and stop.rect.bottom >= 0:
                        yflag = True

        self.handle_input(xflag, yflag)

class Auto(Camera):
    def __init__(self, game_objects, true_scroll = [0,0]):
        super().__init__(game_objects, true_scroll)

    def update(self):
        self.true_scroll[0]+=(self.game_objects.player.rect.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        super().update()

    def handle_input(self,xflag, yflag):
        if xflag and yflag:
            self.set_camera('Fixed')
        elif xflag:
            self.set_camera('Auto_CapX')
        elif yflag:
            self.set_camera('Auto_CapY')

class Auto_CapX(Camera):
    def __init__(self, game_objects, true_scroll = [0,0]):
        true_scroll[0] = 0
        super().__init__(game_objects, true_scroll)

    def update(self):
        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        super().update()

    def handle_input(self,xflag, yflag):
        if xflag and yflag:
            self.set_camera('Fixed')
        elif not xflag:
            self.set_camera('Auto')
        elif yflag:
            self.set_camera('Auto_CapY')

class Auto_CapY(Camera):
    def __init__(self, game_objects, true_scroll = [0,0]):
        true_scroll[1] = 0
        super().__init__(game_objects, true_scroll)

    def update(self):
        self.true_scroll[0]+=(self.game_objects.player.rect.center[0]-8*self.true_scroll[0]-self.center[0])/15
        super().update()

    def handle_input(self,xflag, yflag):
        if xflag and yflag:
            self.set_camera('Fixed')
        elif xflag:
            self.set_camera('Auto_CapX')
        elif not yflag:
            self.set_camera('Auto')

class Fixed(Camera):
    def __init__(self, game_objects, true_scroll):
        super().__init__(game_objects, [0,0])

    def update(self):
        super().update()

    def handle_input(self,xflag, yflag):
        if not xflag and not yflag:
            self.set_camera('Auto')
        elif not xflag:
            self.set_camera('Auto_CapY')
        elif not yflag:
            self.set_camera('Auto_CapX')

class Camera_shake(Camera):
    def __init__(self, curr_camera,amp,duration):
        super().__init__(curr_camera.game_objects)
        self.curr_camera = curr_camera
        self.amp = amp
        self.duration = duration

    def update(self):
        self.duration -= 1
        
        self.curr_camera.shake[0] = random.randint(-self.amp,self.amp)
        self.curr_camera.shake[1] = random.randint(-self.amp,self.amp)
        self.curr_camera.update()
        self.scroll = self.curr_camera.scroll#update the calculated scroll

        self.exit_state()

    def exit_state(self):#go back to the cameera we came from
        if self.duration < 0:
            self.curr_camera.shake = [0,0]
            self.set_camera(type(self.curr_camera).__name__)

#cutscenes
class Deer_encounter(Auto):
    def __init__(self, game_objects,true_scroll):
        super().__init__(game_objects,true_scroll)

    def update(self):
        self.center[0] -= 5
        self.center[0] = max(300,self.center[0])
        super().update()

    def exit_state(self):
        self.set_camera('Auto')

class Cultist_encounter(Auto):
    def __init__(self, game_objects,true_scroll):
        super().__init__(game_objects,true_scroll)

    def update(self):
        self.center[0] += 2
        self.center[0] = min(500,self.center[0])
        super().update()

    def exit_state(self):
        self.set_camera('Auto')

class New_game(Auto):
    def __init__(self, game_objects,true_scroll):
        super().__init__(game_objects,true_scroll)
        self.center[1] = 1000

    def update(self):
        self.center[1] -= 2
        self.center[1] = max(self.game_objects.map.PLAYER_CENTER[1],self.center[1])
        super().update()

    def exit_state(self):
        self.set_camera('Auto')

class Title_screen(Auto):
    def __init__(self, game_objects,true_scroll):
        super().__init__(game_objects,true_scroll)

    def update(self):
        self.center[1] += 2
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.check_camera_border()
        self.scroll=self.true_scroll.copy()
        self.scroll[1]=int(self.scroll[1])+self.shake[1]

    def exit_state(self):
        self.set_camera('Auto')
