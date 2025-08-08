import pygame, sys, time
import game_objects
import constants as C
import read_files
import state_manager
from pygame_render import RenderEngine
import screen_manager
#pygame.print_debug_info()
import statistics
import numpy as np

class Game():
    def __init__(self):
        #initiate all screens
        self.window_size = C.window_size.copy()
        self.scale = self.scale_size(2)#get the scale according to your display size
        display_size = [int(self.window_size[0] * self.scale), int(self.window_size[1] * self.scale)]
        game_settings = read_files.read_json('game_settings.json')['display']

        self.display = RenderEngine(display_size[0] - self.scale, display_size[1] - self.scale, fullscreen = game_settings['fullscreen'], vsync = game_settings['vsync'])        
        self.screen_manager = screen_manager.ScreenManager(self)
        self.screen = self.display.make_layer(self.window_size)#the "main" screen ''rendered last''

        #initiate game related values
        self.game_loop = GameLoop(self)
        self.game_objects = game_objects.Game_Objects(self)
        self.state_manager = state_manager.State_manager(self, 'Title_menu')

        #debug flags
        self.DEBUG_MODE = True
        self.RENDER_FPS_FLAG = True
        self.RENDER_HITBOX_FLAG = True
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN])
        pygame.event.set_blocked([pygame.TEXTINPUT])#for some reason, there is a text input here and there. So, blocking it

    def event_loop(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.game_objects.controller.map_inputs(event)#makes a list of inputs (input buffer)

        self.game_objects.controller.continuous_input_checks()#check every frame independent of event: right, left, up, down
        #self.state_stack[-1].continuous_input_checks()#tdiscrete_inputs_UI is inprinciple not needed for gameplay state
        inputs = self.game_objects.controller.input_buffer.copy()
        self.game_objects.input_interpreter.update(dt)#checks for flicks and other input related things
        for input in inputs:
            input.update(dt)
            self.state_manager.handle_events(input)

    def run(self):
        self.game_loop.run()

    def scale_size(self, scale = None):
        if not scale:#if None
            scale_w = pygame.display.Info().current_w/self.window_size[0]
            scale_h = pygame.display.Info().current_h/self.window_size[1]
            return min(scale_w, scale_h)
        return scale

class GameLoop():
    def __init__(self, game):
        self.game = game
        self.clock = pygame.time.Clock()  
        self.fixed_dt = 1.0 / 60.0  # 60Hz physics step
        self.accumulator = 0.0              
        self.alpha = self.accumulator / self.fixed_dt
        self.dt = 1.0  # Initialize filtered dt (in 60Hz units)
        self.filter_alpha = 0.05  # Smoothing factor (lower = smoother)

    def run(self):
        prev_time = time.perf_counter()
        frame_stats = FrameStats()
        
        while True:
            self.game.screen.clear(0, 0, 0, 0)
            for screen in list(self.game.screen_manager.screens.values()):
                screen.layer.clear(0, 0, 0, 0)                        

            # Calculate raw frame time
            frame_end = time.perf_counter()
            raw_frame_time = 1/max(self.clock.get_fps(),30)
            #raw_frame_time = min(frame_end - prev_time, 2.0 / C.fps)  # Cap to prevent large jumps
            prev_time = frame_end
            
            # Convert to 60Hz units and apply minimum threshold
            raw_dt = max(raw_frame_time * 60, 0.1)
            
            # Apply low-pass filter to smooth dt
            self.dt = (self.filter_alpha * raw_dt) + (1 - self.filter_alpha) * self.dt
            
            # Convert back to seconds for accumulator
            filtered_frame_time = self.dt / 60.0
            
            # Record stats using raw time for accuracy
            frame_stats.record_frame(raw_frame_time)
            
            # Use filtered time for accumulator
            self.accumulator += filtered_frame_time

            # Event handling with filtered dt
            self.game.event_loop(self.dt)

            # Fixed timestep update(s)
            while self.accumulator >= self.fixed_dt:
                self.game.state_manager.update(self.fixed_dt * 60)
                self.accumulator -= self.fixed_dt

            # Render with interpolation
            self.alpha = self.accumulator / self.fixed_dt
            self.game.state_manager.update_render(self.dt)
            self.game.state_manager.render()

            # Render to display
            self.game.screen_manager.render()
            self.game.display.render(self.game.screen.texture, self.game.display.screen, scale=self.game.scale)
            pygame.display.flip()
            
            # Frame rate limiting at the END
            self.clock.tick(C.fps)

class FrameStats:
    def __init__(self, log_interval=3.0, max_samples=300):
        self.frame_times = []
        self.log_interval = log_interval
        self.max_samples = max_samples
        self._log_timer = 0.0
        self._last_log_time = time.perf_counter()

    def record_frame(self, frame_time_sec):
        ms = frame_time_sec * 1000  # convert to milliseconds
        self.frame_times.append(ms)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)

        now = time.perf_counter()
        self._log_timer += now - self._last_log_time
        self._last_log_time = now

        if self._log_timer >= self.log_interval:
            self._log_timer = 0.0
            self.log_stats()

    def log_stats(self):
        if not self.frame_times:
            return
        
        # Basic stats
        avg = statistics.mean(self.frame_times)
        stddev = statistics.stdev(self.frame_times) if len(self.frame_times) > 1 else 0.0
        worst = max(self.frame_times)
        best = min(self.frame_times)
        
        print(f"[Frame Stats] Avg: {avg:.2f} ms | Jitter: ±{stddev:.2f} ms | Best: {best:.2f} ms | Worst: {worst:.2f} ms")
        
        # Advanced smoothness metrics
        self.analyze_smoothness()

    def analyze_smoothness(self):
        if len(self.frame_times) < 10:
            return
            
        # 1. Frame Time Consistency (frame-to-frame variation)
        consistency = self.measure_frame_consistency()
        
        # 2. Target Deviation (how far from ideal 16.67ms for 60fps)
        target_deviation = self.measure_target_deviation()
        
        # 3. Stutter Detection
        stutter_rate = self.detect_stutters()
        
        # 4. Distribution Analysis
        spread = self.analyze_distribution()
        
        # 5. Overall Smoothness Score
        smoothness_score = self.calculate_smoothness_score(consistency, target_deviation, stutter_rate, spread)
        
        print(f"[Smoothness] Consistency: {consistency:.3f} | Target Dev: {target_deviation:.2f} | Stutters: {stutter_rate:.1f}% | Spread: {spread:.2f} | Score: {smoothness_score:.3f}")

    def measure_frame_consistency(self):
        """Measure frame-to-frame time consistency (lower = smoother)"""
        intervals = [abs(self.frame_times[i+1] - self.frame_times[i]) 
                    for i in range(len(self.frame_times)-1)]
        return statistics.stdev(intervals) if len(intervals) > 1 else 0.0

    def measure_target_deviation(self):
        """Average deviation from target 60fps frame time"""
        target_frame_time = 16.67  # 60fps target
        deviations = [abs(ft - target_frame_time) for ft in self.frame_times]
        return statistics.mean(deviations)

    def detect_stutters(self, threshold=2.0):
        """Detect frames that are significantly off from median"""
        if len(self.frame_times) < 5:
            return 0.0
        median = statistics.median(self.frame_times)
        stutters = [ft for ft in self.frame_times if abs(ft - median) > threshold]
        return len(stutters) / len(self.frame_times) * 100

    def analyze_distribution(self):
        """Analyze frame time distribution (95th percentile spread)"""
        sorted_times = sorted(self.frame_times)
        p95_idx = int(len(sorted_times) * 0.95)
        median_idx = len(sorted_times) // 2
        
        p95 = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        median = sorted_times[median_idx]
        
        return p95 - median  # Tighter spread = smoother

    def calculate_smoothness_score(self, consistency, target_deviation, stutter_rate, spread):
        """Combined smoothness score (lower = smoother)"""
        # Weight the different metrics
        score = (consistency * 2.0 +          # Frame consistency is most important
                target_deviation * 1.0 +      # Target deviation
                stutter_rate * 0.1 +          # Stutter rate
                spread * 0.5)                 # Distribution spread
        return score


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 2, 4096)#should result in better sound if this init before pygame.init()
    pygame.init()#initilise
    g = Game()
    g.run()