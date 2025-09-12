import pygame
from engine.utils import read_files
from gameplay.entities.interactables.monuments.base.challenges import Challenges

class ChallengeMonument(Challenges):#the status spawning a portal, balls etc - challange rooms
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/challenges/challenge_monument/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID = ID
        self.interacted = self.game_objects.world_state.quests.get(ID, False)
        self.dialogue = dialogue.Dialogue_interactable(self, ID)#handles dialoage and what to say

        if self.interacted:
            self.shader_state = states_shader.Tint(self, colour = [0,0,0,100])
        else:
            game_objects.lights.add_light(self)
            self.shader_state = states_shader.Idle(self)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest(self.ID.capitalize(), monument = self)

