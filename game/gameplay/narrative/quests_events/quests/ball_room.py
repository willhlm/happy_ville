from gameplay.narrative.quests_events.base import Tasks
from gameplay.entities.projectiles import BouncyBalls
from gameplay.ui.components.overlay.timer import Timer


class BallRoom(Tasks):#the room with ball in light forest cavee
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.description = 'destroy all balls within a given time'
        self.monument = kwarg['monument']
        self.time = 600

    def initiate_quest(self):#called when interact with monument
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_ACTIVE)
        self.timer = Timer(self, self.time)
        self.game_objects.cosmetics.add(self.timer)
        pos = self.monument.rect.center
        self.number = 5#number of balls
        self.spawn_balls(pos)
        self.get_gates()

        self.game_objects.signals.subscribe('ball_killed', self.increase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def spawn_balls(self, pos):
        for i in range(0, self.number):
            new_ball = BouncyBalls((pos[0],pos[1] - 20), self.game_objects, lifetime = self.time)
            self.game_objects.projectiles.add_enemy(new_ball)

    def get_gates(self):#trap aila
        self.game_objects.signals.emit('ball_room_1')
        self.game_objects.signals.emit('ball_room_2')


    def time_out(self):#when timer runs out: fail
        self.timer.kill()
        self.game_objects.signals.emit('ball_room_1')
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_FAILED)
        self.monument.reset()
        self.cleanup()

    def increase_kill(self):#called wgeb ball is destroyed
        self.number -= 1
        if self.number <= 0:
            self.complete()

    def complete(self):
        self.timer.kill()
        self.cleanup()
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_COMPLETED)
        self.game_objects.signals.emit('ball_room_1')
        self.game_objects.signals.emit('ball_room_2')

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('ball_killed', self.increase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)
