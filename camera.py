import random, sys

class Camera_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.camera = Camera(game_objects)# The default camera
        self.decorators = []# List of decorators
        self.stop_handeler = Stop_handeler(game_objects)#is put here so that it only has to be loaded once        

    def set_camera(self, camera, **kwarg):
        self.camera = getattr(sys.modules[__name__], camera)(self.game_objects, self.camera.true_scroll, **kwarg)

    def add_decorator(self, decorator):#e.g. shake
        self.decorators.append(decorator)

    def remove_decorator(self, decorator):#e.g. shake
        self.decorators.remove(decorator)

    def update(self):
        self.camera.update()
        for decorator in self.decorators:
            decorator.update()

    def zoom(self, scale = 1, center = (0.5, 0.5), rate = 1):
        self.game_objects.shader_render.append_shader('zoom', scale = scale, center = center, rate = rate)

    def camera_shake(self, **kwarg):
        self.add_decorator(Camera_shake_decorator(self.camera, **kwarg))
        self.game_objects.controller.rumble(duration = 10 * kwarg.get('duration', 100))

    def reset_player_center(self):#called when loading a map in maploader
        self.camera.reset_player_center()

    def set_camera_position(self):
        self.camera.set_camera_position()

class Camera():#default camera
    def __init__(self, game_objects, scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = scroll
        self.scroll = self.true_scroll.copy()
        self.center = [game_objects.map.PLAYER_CENTER[0] - game_objects.player.rect[2]*0.5, game_objects.map.PLAYER_CENTER[1] - game_objects.player.rect[3]*0.5]
        self.original_center = self.center.copy()        

    def update(self):
        self.game_objects.camera_manager.stop_handeler.update()#centeralised sometimes the camera, if there is no more camera stops left        

        self.true_scroll[0] += (self.game_objects.player.true_pos[0] - self.true_scroll[0] - self.center[0])*0.1
        self.true_scroll[1] += (self.game_objects.player.true_pos[1] - self.true_scroll[1] - self.center[1])*0.1
        self.scroll = self.true_scroll.copy()

        self.scroll[0] = int(self.scroll[0])
        self.scroll[1] = int(self.scroll[1])

    def reset_player_center(self):#called when loading a map in maploader
        self.center = self.original_center.copy()
        self.game_objects.camera_manager.stop_handeler.reset()
        for stop in self.game_objects.camera_blocks:#apply cameras stopp
            stop.update()
            stop.currentstate.init_pos()
        self.set_camera_position()

    def set_camera_position(self):
        self.true_scroll = [self.game_objects.player.true_pos[0] - self.center[0], self.game_objects.player.true_pos[1] - self.center[1]]#-self.game_objects.player.rect[2]*0.5,-self.game_objects.player.rect[3]*0.5 if there was a camera stopp

class No_camera(Camera):
    def __init__(self, game_objects, scroll, **kwarg):
        super().__init__(game_objects, scroll)   

    def camera_shake(self, **kwarg):
        pass          

    def update(self):
        pass

    def exit_state(self):#go back to the cameera
        self.game_objects.camera_manager.set_camera('Camera')       

#decorators
class Camera_shake_decorator():
    def __init__(self, current_camera, **kwarg):
        self.current_camera = current_camera
        self.amp = kwarg.get('amplitude', 10)
        self.duration = kwarg.get('duration', 100)
        self.scale = kwarg.get('scale', 0.98)         

    def update(self):
        self.amp *= self.scale
        self.current_camera.scroll[0] += random.uniform(-self.amp, self.amp)
        self.current_camera.scroll[1] += random.uniform(-self.amp, self.amp)
        self.duration -= self.current_camera.game_objects.game.dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.current_camera.game_objects.camera_manager.remove_decorator(self)

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
        target = self.game_objects.camera_manager.camera.original_center[0]   

        if self.game_objects.camera_manager.camera.center[0] - target > 0:
            self.game_objects.camera_manager.camera.center[0] -= self.game_objects.game.dt*2
            self.game_objects.camera_manager.camera.center[0] = max(target, self.game_objects.camera_manager.camera.center[0])
        else:
            self.game_objects.camera_manager.camera.center[0] += self.game_objects.game.dt*2
            self.game_objects.camera_manager.camera.center[0] = min(target, self.game_objects.camera_manager.camera.center[0])

        if self.game_objects.camera_manager.camera.center[0] == target:#if finished
            self.updates.remove(self.recenteralise_horizontal)

    def recenteralise_vertical(self):
        target = self.game_objects.camera_manager.camera.original_center[1]
        
        if self.game_objects.camera_manager.camera.center[1]-target > 0:#camera is below
            self.game_objects.camera_manager.camera.center[1] -= self.game_objects.game.dt*2
            self.game_objects.camera_manager.camera.center[1] = max(target, self.game_objects.camera_manager.camera.center[1])
        else:#camera is above
            self.game_objects.camera_manager.camera.center[1] += self.game_objects.game.dt*2
            self.game_objects.camera_manager.camera.center[1] = min(target, self.game_objects.camera_manager.camera.center[1])

        if self.game_objects.camera_manager.camera.center[1] == target:#if finished
            self.updates.remove(self.recenteralise_vertical)

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update_stop(self):
        for stop in self.game_objects.camera_blocks:
            stop.update()

    def exit_state(self):#called from cutscenes
        self.game_objects.camera_manager.set_camera('Camera')

class Deer_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

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
        self.center = [self.game_objects.camera_manager.camera.center[0],1000]#[176,230]
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
        self.scroll = self.true_scroll.copy()
        self.scroll[1] = int(self.scroll[1])        