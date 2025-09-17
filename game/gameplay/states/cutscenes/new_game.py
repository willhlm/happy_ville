from .base.cutscene_engine import CutsceneEngine

class NewGame(CutsceneEngine):#first screen to be played when starying a new game -> needs to be called after that the map has loaded
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.camera_manager.set_camera('New_game')#when starting a new game, should be a cutscene
        self.camera_stops = []#temporary remove the came stops
        for camera_stop in self.game.game_objects.camera_blocks:
            self.camera_stops.append(camera_stop)
        self.game.game_objects.camera_blocks.empty()

    def cinematic(self):
        pass

    def update(self, dt):
        super().update(dt)
        self.timer += dt
        if self.timer > 500:
            self.game.state_manager.exit_state()

    def on_exit(self):
        for camera_stop in self.camera_stops:
            self.game.game_objects.camera_blocks.add(camera_stop)
        self.game.game_objects.camera_manager.camera.exit_state()
        super().on_exit()
