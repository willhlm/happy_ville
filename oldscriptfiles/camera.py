import random, sys

class Camera():
    def __init__(self, game_objects, scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = scroll
        self.scroll = self.true_scroll.copy()
        self.center = [game_objects.map.PLAYER_CENTER[0] - game_objects.player.rect[2]*0.5, game_objects.map.PLAYER_CENTER[1] - game_objects.player.rect[3]*0.5]
        self.original_center = self.center.copy()        

    def update(self):
        self.game_objects.stop_handeler.update()#centeralised sometimes the camera, if there is no more camera stops left        

        self.true_scroll[0] += (self.game_objects.player.true_pos[0] - self.true_scroll[0] - self.center[0])*0.1
        self.true_scroll[1] += (self.game_objects.player.true_pos[1] - self.true_scroll[1] - self.center[1])*0.1
        self.scroll = self.true_scroll.copy()

        self.scroll[0] = int(self.scroll[0])
        self.scroll[1] = int(self.scroll[1])

    def set_camera(self, camera, **kwarg):
        self.game_objects.camera = getattr(sys.modules[__name__], camera)(self.game_objects, self.true_scroll, **kwarg)

    def camera_shake(self, **kwarg):
        self.game_objects.camera = Camera_shake(self.game_objects, self.true_scroll, **kwarg)

    def reset_player_center(self):#called when loading a map in maploader
        self.center = self.original_center.copy()
        self.game_objects.stop_handeler.reset()
        for stop in self.game_objects.camera_blocks:#apply cameras stopp
            stop.update()
            stop.currentstate.init_pos()
        self.set_camera_position()

    def set_camera_position(self):
        self.true_scroll = [self.game_objects.player.true_pos[0] - self.center[0], self.game_objects.player.true_pos[1] - self.center[1]]#-self.game_objects.player.rect[2]*0.5,-self.game_objects.player.rect[3]*0.5 if there was a camera stopp

    def zoom(self, scale = 1, center = (0.5, 0.5), rate = 1):
        self.game_objects.shader_render.append_shader('zoom', scale = scale, center = center, rate = rate)

    def exit_state(self):
        pass

class Camera_shake(Camera):
    def __init__(self, game_objects, scroll, **kwarg):
        super().__init__(game_objects, scroll)
        self.amp = kwarg.get('amplitude', 3)
        self.duration = kwarg.get('duration', 100)
        self.scale = kwarg.get('scale', 0.9)

    def camera_shake(self, **kwarg):
        self.amp = kwarg.get('amplitude', 3)
        self.duration = kwarg.get('duration', 100)   
        self.scale = kwarg.get('scale', 0.9)             

    def update(self):
        super().update()
        self.amp = self.scale * self.amp
        self.scroll[0] += random.uniform(-self.amp,self.amp)
        self.scroll[1] += random.uniform(-self.amp,self.amp)
        self.duration -= self.game_objects.game.dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.set_camera('Camera')

class No_camera(Camera):
    def __init__(self, game_objects, scroll, **kwarg):
        super().__init__(game_objects, scroll)   

    def camera_shake(self, **kwarg):
        pass          

    def update(self):
        pass

    def exit_state(self):#go back to the cameera
        self.set_camera('Camera')         

class Stop_handeler():#depending on active camera stops, the re centeralisation can be called
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.reset()
        self.updates = []

    def reset(self):
        self.stops = {'bottom':0,'top':0,'left':0,'right':0,'center':0}#counds number of active stops, setted in camera stop states

    def update(self):#called from camera, in case the camera needs to be re centeralised        
        for update in self.updates:
            update()

    def add_stop(self,stop):#called from camera stop states
        self.stops[stop] += 1

        if stop == 'bottom' or stop == 'top' or stop == 'center':
            if self.recenteralise_vertical in self.updates:
              self.updates.remove(self.recenteralise_vertical)

        if stop =='right' or stop =='left' or stop == 'center':
            if self.recenteralise_horizontal in self.updates:
                self.updates.remove(self.recenteralise_horizontal)

    def remove_stop(self,stop):#called from camera stop states
        self.stops[stop] -= 1        
        if self.stops['bottom'] == 0 and self.stops['top'] == 0 and self.stops['center'] == 0:
            self.updates.append(self.recenteralise_vertical)            
        elif self.stops['left'] == 0 and self.stops['right'] == 0 and self.stops['center'] == 0:
            self.updates.append(self.recenteralise_horizontal)

    def recenteralise_horizontal(self):
        target = self.game_objects.camera.original_center[0]   

        if self.game_objects.camera.center[0] - target > 0:
            self.game_objects.camera.center[0] -= self.game_objects.game.dt*2
            self.game_objects.camera.center[0] = max(target, self.game_objects.camera.center[0])
        else:
            self.game_objects.camera.center[0] += self.game_objects.game.dt*2
            self.game_objects.camera.center[0] = min(target, self.game_objects.camera.center[0])

        if self.game_objects.camera.center[0] == target:#if finished
            self.updates.remove(self.recenteralise_horizontal)

    def recenteralise_vertical(self):
        target = self.game_objects.camera.original_center[1]
        if self.game_objects.camera.center[1]-target > 0:#camera is below
            self.game_objects.camera.center[1] -= self.game_objects.game.dt*2
            self.game_objects.camera.center[1] = max(target, self.game_objects.camera.center[1])
        else:#camera is above
            self.game_objects.camera.center[1] += self.game_objects.game.dt*2
            self.game_objects.camera.center[1] = min(target, self.game_objects.camera.center[1])

        if self.game_objects.camera.center[1] == target:#if finished
            self.updates.remove(self.recenteralise_vertical)

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)
        self.shaking = False

    def update(self):
        super().update()
        self.shakeit()

    def camera_shake(self,**kwarg):#if camera shake is called during a cutscene, set a flag so that it shakes
        self.shaking = True
        self.amp = kwarg.get('amplitude', 3)
        self.duration = kwarg.get('duration', 100)
        self.scale = kwarg.get('scale', 0.9)

    def shakeit(self):
        if not self.shaking: return
        self.duration -= self.game_objects.game.dt
        self.scroll[0] += random.randint(-self.amp,self.amp)
        self.scroll[1] += random.randint(-self.amp,self.amp)
        if self.duration < 0:
            self.shaking = False

    def update_stop(self):
        for stop in self.game_objects.camera_blocks:
            stop.update()

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
        self.update_stop()
        self.center = [self.game_objects.camera.center[0],1000]#[176,230]
        self.set_camera_position()

    def update(self):
        self.center[1] -= 2*self.game_objects.game.dt
        self.center[1] = max(230,self.center[1])
        super().update()

class Title_screen(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self):
        self.center[1] += 2*self.game_objects.game.dt
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1] += (self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.scroll=self.true_scroll.copy()
        self.scroll[1]=int(self.scroll[1])        