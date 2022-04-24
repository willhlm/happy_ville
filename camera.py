import random, sys

class Camera():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.scroll=[0,0]
        self.true_scroll=[0,0]
        self.center = list(game_objects.player_center)
        self.shake=[0,0]

    def update(self):
        self.check_camera_border()
        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+self.shake[0]
        self.scroll[1]=int(self.scroll[1])+self.shake[1]

    def set_camera(self, camera):
        new_camera=getattr(sys.modules[__name__], camera)(self.game_objects)
        self.game_objects.camera.append(new_camera)

    def exit_state(self):
        self.game_objects.camera.pop()

    def check_camera_border(self):
        xflag, yflag = False, False
        for stop in self.game_objects.camera_blocks:
            if stop.dir == 'right':
                if (self.game_objects.player.hitbox.centery - stop.rect.bottom < self.game_objects.player_center[1]) and (stop.rect.top - self.game_objects.player.hitbox.centery < self.game_objects.game.WINDOW_SIZE[1] - self.game_objects.player_center[1]):
                    #if -self.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.player.hitbox.centerx) < self.player_center[0]:
                    if -self.game_objects.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.game_objects.player_center[0]) < self.game_objects.player_center[0] and self.game_objects.player.hitbox.centerx >= self.game_objects.player_center[0]:
                        xflag = True
            elif stop.dir == 'left':
                if stop.rect.right >= 0 and self.game_objects.player.hitbox.centerx < self.game_objects.player_center[0]:
                    xflag = True
            elif stop.dir == 'bottom':
                if (stop.rect.left - self.game_objects.player.hitbox.centerx < self.game_objects.player_center[0]) and (self.game_objects.player.hitbox.centerx - stop.rect.right < self.game_objects.player_center[0]):
                    if (-self.game_objects.game.WINDOW_SIZE[1] < (stop.rect.centery - self.game_objects.player.hitbox.centery) < (self.game_objects.game.WINDOW_SIZE[1] - self.game_objects.player_center[1])):
                        yflag = True
            elif stop.dir == 'top':
                if (0 < stop.rect.left - self.game_objects.player.hitbox.centerx < self.game_objects.player_center[0]) or (0 < self.game_objects.player.hitbox.centerx - stop.rect.right < self.game_objects.player_center[0]):
                    if self.game_objects.player.hitbox.centery - stop.rect.centery < 180 and stop.rect.bottom >= 0:
                        yflag = True

        self.handle_input(xflag, yflag)

class Auto(Camera):
    def __init__(self, game_objects):
        super().__init__(game_objects)

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
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        super().update()

    def handle_input(self,xflag, yflag):
        if xflag and yflag:
            self.set_camera('Fixed')
        elif not xflag:
            self.exit_state()
        elif yflag:
            self.set_camera('Auto_CapY')

class Auto_CapY(Camera):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.true_scroll[0]+=(self.game_objects.player.rect.center[0]-8*self.true_scroll[0]-self.center[0])/15
        super().update()

    def handle_input(self,xflag, yflag):
        if xflag and yflag:
            self.set_camera('Fixed')
        elif xflag:
            self.set_camera('Auto_CapX')
        elif not yflag:
            self.exit_state()

class Fixed(Camera):
    def __init__(self):
        super().__init__()

    def update(self):
        super().update()

    def handle_input(self,xflag, yflag):
        if not xflag and not yflag:
            self.exit_state()

class Camera_shake(Auto):
    def __init__(self, center,amp=3):
        super().__init__(center)
        self.amp=amp

    def update(self):
        self.shake[0]=random.randint(-self.amp,self.amp)
        self.shake[1]=random.randint(-self.amp,self.amp)
        super().update()

    def exit_state(self):
        super().exit_state()
        self.shake=[0,0]

class Deer_encounter(Auto):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[0]-=5
        self.center[0]=max(100,self.center[0])
        super().update()