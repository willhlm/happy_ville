from enum import Enum, auto
import time


class States(Enum):
    IDLE = auto()
    CHASE = auto()
    ATTACK = auto()
    DEATH = auto()


class GameObject:
    def __init__(self):
        self.state = States.IDLE
        print(self.state)
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state


class Entity(GameObject):
    def __init__(self):
        super().__init__()
        self.__health = 100

    def sub_health(self):
        self.__health -= 20

    def get_health(self):
        return self.__health

    def set_health(self, health):
        self.__health = health


player = Entity()
player.set_state(States.ATTACK)

enemy = Entity()
enemy.set_health(200)
enemy.set_state(States.CHASE)
