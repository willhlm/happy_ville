import pygame
from engine.utils import read_files
from gameplay.entities.interactables.statues.quests.base.statues import Statues

class StoneWood(Statues):#the stone "statue" to initiate the lumberjacl quest
    def __init__(self, pos, game_objects, quest, item):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/challenges/stone_wood/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.item = item
        self.quest = quest

        self.interacted = self.game_objects.world_state.quests.get(quest, False)
        self.dialogue = dialogue.Dialogue_interactable(self, quest)#handles dialoage and what to say
        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self)

    def on_interact(self, item, player):#called when the signal is emitted
        if type(item).__name__.lower() == self.item:
            self.game_objects.quests_events.initiate_quest(self.quest, item = self.item)

    def buisness(self):#enters after conversation
        self.game_objects.signals.subscribe('item_interacted', self.on_interact)
        item = getattr(sys.modules[__name__], self.item.capitalize())(self.rect.center, self.game_objects, state = 'wild')#make a class based on the name of the newstate: need to import sys
        self.game_objects.loot.add(item)

