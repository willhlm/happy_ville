import pygame
from engine.utils import read_files
from gameplay.entities.interactables.statues.quests.base.statues import Statues
from gameplay.narrative import dialogue
from gameplay.entities.shared.states import states_shader

class QuestStatue(Statues):#the status spawning a portal, balls etc - challange rooms
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/statues/quests/challenge_monument/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID = ID
        self.interacted = self.game_objects.world_state.narrative.is_quest_completed(ID)
        self.dialogue = dialogue.Dialogue(
            self,
            data_path = "gameplay/narrative/text/interactables/" + ID + ".json",
            speaker_id = "interactable:" + ID,
            allow_comments = False,
        )#handles dialoage and what to say

        if self.interacted:
            self.shader_state = states_shader.Tint(self, colour = [0,0,0,100])
        else:
            game_objects.lights.add_light(self)
            self.shader_state = states_shader.Idle(self)

    def on_conversation_complete(self):
        self.game_objects.quests_events.initiate_quest(self.ID, monument = self)
