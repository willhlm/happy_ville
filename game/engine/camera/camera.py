import random, sys
from . import states_centraliser

class Camera_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.camera = Camera(game_objects)# The default camera
        self.decorators = []# List of decorators
        self.look_offset = states_centraliser.LookOffsetController(self)

    def set_camera(self, camera, **kwarg):
        self.camera = getattr(sys.modules[__name__], camera)(self.game_objects, self.camera.true_scroll, **kwarg)

    def add_decorator(self, decorator):#e.g. shake
        self.decorators.append(decorator)

    def remove_decorator(self, decorator):#e.g. shake
        self.decorators.remove(decorator)

    def update_render(self, dt):
        self.camera.update_render(dt)  
        for decorator in self.decorators:
            decorator.update(dt)

    def update(self, dt):
        self.look_offset.update(dt)
        self.camera.update(dt)  
        
    def zoom_out(self, **kwarg):
        self.game_objects.post_process.shaders['zoom'].zoom_out(**kwarg)

    def zoom(self, scale = 1, center = (0.5, 0.5), rate = 1):
        self.game_objects.post_process.append_shader('zoom', scale = scale, center = center, rate = rate)

    def camera_shake(self, **kwarg):#shake dat ass
        self.add_decorator(Camera_shake_decorator(self.camera, **kwarg))
        self.game_objects.controller.rumble(duration = 10 * kwarg.get('duration', 100))

    def reset_player_center(self):#called when loading a map in maploader
        self.camera.reset_player_center()

    def set_camera_position(self):
        self.camera.set_camera_position()

    def handle_movement(self, axes):#right analogue stick: called from gameplay state
        self.camera.handle_movement(axes)

class Camera():#default camera
    def __init__(self, game_objects, scroll = [0,0]):
        self.game_objects = game_objects
        self.true_scroll = scroll
        self.scroll = self.true_scroll.copy()
        self.prev_true_scroll = self.true_scroll.copy()
        self.interp_scroll = self.true_scroll.copy()
        self.y_offset = 30
        self.center = [game_objects.game.viewport_center[0] - game_objects.player.rect[2]*0.5, game_objects.game.viewport_center[1] - game_objects.player.rect[3]*0.5 + self.y_offset]
        self.original_center = self.center.copy()
        self.target = self.original_center.copy()
        self.target_scroll = scroll.copy()

    def update(self, dt):
        self.center = self._solve_center()
        target_x = self.target_scroll[0]
        target_y = self.target_scroll[1]

        # Smooth towards player once per physics step   
        self.prev_true_scroll = self.true_scroll.copy()
        self.true_scroll[0] += (target_x - self.true_scroll[0]) * 0.1
        self.true_scroll[1] += (target_y - self.true_scroll[1]) * 0.1

    def update_render(self, dt):
        alpha = self.game_objects.game.game_loop.alpha
        self.interp_scroll = [self.prev_true_scroll[0] + (self.true_scroll[0] - self.prev_true_scroll[0]) * alpha, self.prev_true_scroll[1] + (self.true_scroll[1] - self.prev_true_scroll[1]) * alpha]        
        self.scroll = [int(self.interp_scroll[0]),int(self.interp_scroll[1])]    

    def reset_player_center(self):#called when loading a map in maploader
        self.game_objects.camera_manager.look_offset.reset()
        self.center = self._solve_center()
        self.set_camera_position()

    def set_camera_position(self):
        self.target_scroll = [
            self.game_objects.player.true_pos[0] - self.center[0],
            self.game_objects.player.true_pos[1] - self.center[1],
        ]
        self.true_scroll = self.target_scroll.copy()
        self.prev_true_scroll = self.true_scroll.copy()
        self.interp_scroll = self.true_scroll.copy()
        self.scroll = [int(self.true_scroll[0]), int(self.true_scroll[1])]

    def handle_movement(self, axes):#right analogue stick        
        self.game_objects.camera_manager.look_offset.handle_movement(axes.look)

    def _solve_center(self):
        self.target_scroll = self._solve_target_scroll()
        player_pos = self.game_objects.player.true_pos
        return [player_pos[0] - self.target_scroll[0], player_pos[1] - self.target_scroll[1]]

    def _solve_target_scroll(self):
        player = self.game_objects.player
        viewport_w, viewport_h = self.game_objects.game.window_size
        base_scroll = self._build_base_scroll(player)
        active_stops = self._get_active_stops(player)
        locked_x = self._select_locked_stop(active_stops, ("center", "center_x"))
        locked_y = self._select_locked_stop(active_stops, ("center", "center_y"))
        min_scroll_x, max_scroll_x, min_scroll_y, max_scroll_y = self._collect_clamp_bounds(active_stops, viewport_w, viewport_h)

        target_x = self._resolve_axis(
            base_scroll[0],
            locked_x.hitbox.centerx - viewport_w * 0.5 if locked_x else None,
            min_scroll_x,
            max_scroll_x,
        )
        target_y = self._resolve_axis(
            base_scroll[1],
            locked_y.hitbox.centery - viewport_h * 0.5 if locked_y else None,
            min_scroll_y,
            max_scroll_y,
        )

        return [target_x, target_y]

    def _build_base_scroll(self, player):
        look_offset = self.game_objects.camera_manager.look_offset.offset
        base_center = [
            self.original_center[0] + look_offset[0],
            self.original_center[1] + look_offset[1],
        ]
        return [
            player.true_pos[0] - base_center[0],
            player.true_pos[1] - base_center[1],
        ]

    def _get_active_stops(self, player):
        return [stop for stop in self.game_objects.camera_blocks if stop.is_active(player)]

    def _collect_clamp_bounds(self, active_stops, viewport_w, viewport_h):
        min_scroll_x = None
        max_scroll_x = None
        min_scroll_y = None
        max_scroll_y = None

        for stop in active_stops:
            if stop.mode == "left":
                min_scroll_x = max(min_scroll_x, stop.hitbox.left) if min_scroll_x is not None else stop.hitbox.left
            elif stop.mode == "right":
                bound = stop.hitbox.right - viewport_w
                max_scroll_x = min(max_scroll_x, bound) if max_scroll_x is not None else bound
            elif stop.mode == "top":
                min_scroll_y = max(min_scroll_y, stop.hitbox.top) if min_scroll_y is not None else stop.hitbox.top
            elif stop.mode == "bottom":
                bound = stop.hitbox.bottom - viewport_h
                max_scroll_y = min(max_scroll_y, bound) if max_scroll_y is not None else bound

        return min_scroll_x, max_scroll_x, min_scroll_y, max_scroll_y

    def _resolve_axis(self, base_value, locked_value, min_value, max_value):
        if locked_value is not None:
            return locked_value

        target_value = base_value
        if min_value is not None:
            target_value = max(target_value, min_value)
        if max_value is not None:
            target_value = min(target_value, max_value)
        if min_value is not None and max_value is not None and min_value > max_value:
            target_value = (min_value + max_value) * 0.5

        return target_value

    def _select_locked_stop(self, active_stops, modes):
        candidates = [stop for stop in active_stops if stop.mode in modes]
        if not candidates:
            return None
        return max(candidates, key=lambda stop: (stop.priority, -stop.area))

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
        self.original_amp = self.amp
        self.duration = kwarg.get('duration', 100)
        self.length = self.duration
        self.scale = kwarg.get('scale', 0.98)

    def update(self, dt):
        self.amp = (self.original_amp - (1 - self.duration/self.length))*dt#need to be this compicated one to respect any time freeze
        self.current_camera.true_scroll[0] += random.uniform(-self.amp, self.amp)#only stuff relying on scroll will be affected, true scroll like player is not
        self.current_camera.true_scroll[1] += random.uniform(-self.amp, self.amp)
        
        self.duration -= dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.current_camera.game_objects.camera_manager.remove_decorator(self)

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        target_x = self.game_objects.player.true_pos[0] - self.center[0]
        target_y = self.game_objects.player.true_pos[1] - self.center[1]
        self.prev_true_scroll = self.true_scroll.copy()
        self.true_scroll[0] += (target_x - self.true_scroll[0]) * 0.1
        self.true_scroll[1] += (target_y - self.true_scroll[1]) * 0.1

    def update_stop(self):
        pass

    def exit_state(self):#called from cutscenes
        self.game_objects.camera_manager.set_camera('Camera')        

class Deer_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        self.center[0] -= 5*dt
        self.center[0] = max(100,self.center[0])
        super().update(dt)

class Cultist_encounter(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        self.center[0] += 2*dt
        self.center[0] = min(500,self.center[0])
        super().update(dt)

class Start_game(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)
        self.center = [self.game_objects.camera_manager.camera.center[0], 1000]
        self.set_camera_position()

        self.target_y = self.game_objects.camera_manager.camera.center[1] + 16*3# Now use the target they set
        
    def update(self, dt):
        self.center[1] -= 2 * dt
        self.center[1] = max(self.target_y, self.center[1])
        super().update(dt)

class Title_screen(Cutscenes):
    def __init__(self, game_objects, scroll):
        super().__init__(game_objects, scroll)

    def update(self, dt):
        self.center[1] += 2*dt
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1] += (self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.scroll = self.true_scroll.copy()
        self.scroll[1] = int(self.scroll[1])
