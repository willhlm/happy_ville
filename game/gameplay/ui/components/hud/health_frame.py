from .health import Health

class HealthFrame(Health):#gameplay UI
    def __init__(self,game_objects):
        super().__init__(game_objects, 'assets/sprites/ui/hud/health_frame/')

