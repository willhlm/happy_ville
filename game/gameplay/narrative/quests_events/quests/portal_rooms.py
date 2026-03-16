from gameplay.entities.interactables import Portal
from gameplay.narrative.quests_events.base import Tasks


class PortalRooms(Tasks):#challanges with portals
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.monument = kwarg['monument']

    def initiate_room(self):#portal calls it after growing
        pass

    def initiate_quest(self):
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_ACTIVE)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)
        pos = self.monument.rect.center
        self.portal = Portal([pos[0] + 100, pos[1] - 20], self.game_objects, state = self)
        self.game_objects.special_shaders.add(self.portal)

    def put_gate(self):
        self.gates = []

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated
            self.complete()#if there was a gate, we can open it

    def complete(self):
        self.cleanup()
        self.portal.currentstate.handle_input('shrink')
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_COMPLETED)
        for gate in self.gates:
            gate.kill()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)
