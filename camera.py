import random, sys
from states import states_centraliser

class Camera_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.camera = Camera(game_objects)# The default camera
        self.decorators = []# List of decorators
        self.stop_handeler = Stop_handeler(self)#is put here so that it only has to be loaded once
        self.centraliser = states_centraliser.Idle(self)

    def set_camera(self, camera, **kwarg):
        self.camera = getattr(sys.modules[__name__], camera)(self.game_objects, self.camera.true_scroll, **kwarg)

    def add_decorator(self, decorator):#e.g. shake
        self.decorators.append(decorator)

    def remove_decorator(self, decorator):#e.g. shake
        self.decorators.remove(decorator)

    def update_render(self, dt):
        self.camera.update(dt)  
        for decorator in self.decorators:
            decorator.update(dt)

    def zoom(self, scale = 1, center = (0.5, 0.5), rate = 1):
        self.game_objects.shader_render.append_shader('zoom', scale = scale, center = center, rate = rate)

    def camera_shake(self, **kwarg):#shake dat ass
        self.add_decorator(Camera_shake_decorator(self.camera, **kwarg))
        self.game_objects.controller.rumble(duration = 10 * kwarg.get('duration', 100))

    def reset_player_center(self):#called when loading a map in maploader
        self.camera.reset_player_center()

    def set_camera_position(self):
        self.camera.set_camera_position()

    def handle_movement(self, input):#right analogue stick: called from gameplay state
        self.camera.handle_movement(input)

class Camera():#default camera
    def __init__(self, game_objects, scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = scroll
        self.scroll = self.true_scroll.copy()
        self.y_offset = 30
        #self.center = [game_objects.map.PLAYER_CENTER[0] - game_objects.player.rect[2]*0.5, game_objects.map.PLAYER_CENTER[1] - game_objects.player.rect[3]*0.5]
        self.center = [game_objects.map.PLAYER_CENTER[0] - game_objects.player.rect[2]*0.5, game_objects.map.PLAYER_CENTER[1] - game_objects.player.rect[3]*0.5 + self.y_offset]
        self.original_center = self.center.copy()
        self.target = self.original_center.copy()#is set by camera stop, the target position of center for the centraliser

    def update(self, dt):
        alpha = self.game_objects.game.game_loop.alpha  # Interpolation factor based on the accumulator
        self.game_objects.camera_manager.centraliser.update()#camera stop and tight analogue stick can tell it what to do

        # Interpolate player position for smooth camera movement
        interp_x = self.game_objects.player.prev_true_pos[0] + (self.game_objects.player.true_pos[0] - self.game_objects.player.prev_true_pos[0]) * alpha
        interp_y = self.game_objects.player.prev_true_pos[1] + (self.game_objects.player.true_pos[1] - self.game_objects.player.prev_true_pos[1]) * alpha

        self.true_scroll[0] += (interp_x - self.true_scroll[0] - self.center[0]) * 0.1
        self.true_scroll[1] += (interp_y - self.true_scroll[1] - self.center[1]) * 0.1

        self.scroll = [round(self.true_scroll[0]), round(self.true_scroll[1])]

    def reset_player_center(self):#called when loading a map in maploader
        self.center = self.original_center.copy()
        self.game_objects.camera_manager.stop_handeler.reset()
        for stop in self.game_objects.camera_blocks:#apply cameras stopp
            stop.update(0)
            stop.currentstate.init_pos()
        self.set_camera_position()

    def set_camera_position(self):
        self.true_scroll = [self.game_objects.player.true_pos[0] - self.center[0], self.game_objects.player.true_pos[1] - self.center[1]]#-self.game_objects.player.rect[2]*0.5,-self.game_objects.player.rect[3]*0.5 if there was a camera stopp

    def handle_movement(self, event):#right analogue stick        
        self.game_objects.camera_manager.centraliser.handle_movement(event['r_stick'])          

class No_camera(Camera):
    def __init__(self, game_objects, scroll, **kwarg):
        super().__init__(game_objects, scroll)

    def camera_shake(self, **kwarg):
        pass

    def update(self, dt):
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

    def update(self, dt):
        self.amp *= self.scale
        self.current_camera.scroll[0] += random.uniform(-self.amp, self.amp)#only stuff relying on scroll will be affected, true scroll like player is not
        self.current_camera.scroll[1] += random.uniform(-self.amp, self.amp)
        
        self.duration -= dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.current_camera.game_objects.camera_manager.remove_decorator(self)

class Stop_handeler():#counts all active stops. It then tells the centraliser to start
    def __init__(self, camera_manager):
        self.camera_manager = camera_manager
        self.reset()

    def reset(self):#called when changing the map from reset_player_center
        self.stops = {'bottom':0, 'top':0, 'left':0, 'right':0, 'center':0}#counds number of active stops, setted in camera stop states

    def add_stop(self,stop):#called from camera stop states
        self.stops[stop] += 1        
        self.camera_manager.centraliser.handle_input('stop')

    def remove_stop(self,stop):#called from camera stop states
        self.stops[stop] -= 1
        if self.stops['bottom'] == 0 and self.stops['top'] == 0 and self.stops['center'] == 0:
            self.camera_manager.camera.target = self.camera_manager.camera.original_center.copy()#sets the target of centrliser
            self.camera_manager.centraliser.handle_input('start', direction = [0, 1])#veritcal
        elif self.stops['left'] == 0 and self.stops['right'] == 0 and self.stops['center'] == 0:
            self.camera_manager.camera.target = self.camera_manager.camera.original_center.copy()#sets the target of centrliser
            self.camera_manager.centraliser.handle_input('start', direction = [1, 0])#horitocnal

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

    def update(self, dt):
        self.center[0] -= 5*dt
        self.center[0] = max(100,self.center[0])
        super().update()

class Cultist_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        self.center[0] += 2*dt
        self.center[0] = min(500,self.center[0])
        super().update()

class New_game(Cutscenes):#initialised in New_game state
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)
        self.update_stop()
        self.center = [self.game_objects.camera_manager.camera.center[0],1000]#[176,230]
        self.set_camera_position()

    def update(self, dt):
        self.center[1] -= 2*dt
        self.center[1] = max(230,self.center[1])
        super().update()

class Title_screen(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        self.center[1] += 2*dt
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1] += (self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.scroll = self.true_scroll.copy()
        self.scroll[1] = int(self.scroll[1])
