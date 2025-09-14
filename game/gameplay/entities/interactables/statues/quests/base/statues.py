from gameplay.entities.interactables.base.interactables import Interactables

class Statues(Interactables):#monuments you interact to get quests or challenges
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)

    def render_potrait(self, target):
        pass

    def interact(self):#when plater press t
        if self.interacted: return
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)

        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

    def reset(self):#called when challange is failed
        self.shader_state.handle_input('idle')
        self.interacted = False