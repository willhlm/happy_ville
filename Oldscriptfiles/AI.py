class AI():
    def __init__(self,entity):
        self.entity=entity
        self.player_distance=[0,0]
        self.counter =0

    def enter_state(self):
        self.entity.AI_stack.append(self)

    def exit_state(self):
        self.entity.AI_stack.pop()

    def update(self,playerpos):
        self.counter += 1
        self.player_distance[0] = playerpos[0] - self.entity.rect.center[0]

class Peace_AI(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self,playerpos):
        super().update(playerpos)
        self.entity.peaceAI()

class Aggro_AI(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self,playerpos):
        super().update(playerpos)
        self.entity.aggroAI()
