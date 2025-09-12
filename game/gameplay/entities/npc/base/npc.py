import pygame, random
from engine.utils import read_files
from gameplay.narrative import dialogue

from gameplay.entities.base.character import Character
from gameplay.entities.states import states_NPC
from gameplay.entities.cosmetics.cosmetics import InteractableIndicator, ConversationBubbles

class NPC(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.name = str(type(self).__name__)#the name of the npc
        self.load_sprites()
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox

        self.currentstate = states_NPC.Idle(self)
        self.dialogue = dialogue.Dialogue(self)#handles dialoage and what to say
        self.define_conversations()
        self.collided = False
        self.indicator = InteractableIndicator(self.rect.topright, self.game_objects)

    def player_noncollision(self):
        if not self.collided: return
        self.indicator.kill()
        self.collided = False
        
    def player_collision(self, player):        
        if self.collided: return              
        self.game_objects.cosmetics.add(self.indicator)
        self.collided = True

    def define_conversations(self):#should depend on NPC
        self.priority = ['reindeer','ape']#priority events to say
        self.event = ['aslat']#normal events to say
        self.quest = []

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict("assets/sprites/enteties/npc/" + self.name + "/animation/", self.game_objects)
        img = pygame.image.load('assets/sprites/enteties/npc/' + self.name +'/potrait.png').convert_alpha()
        self.portrait = self.game_objects.game.display.surface_to_texture(img)#need to save in memoery

    def update(self, dt):
        super().update(dt)
        #self.group_distance()

    def render_potrait(self, terget):
        self.game_objects.game.display.render(self.portrait, terget, position = (32,32))#shader render

    def interact(self):#when plater press t
        self.game_objects.game.state_manager.enter_state('Conversation', npc = self)#pehrpame make a callback insted of "buissness"

    def random_conversation(self, text):#can say stuff through a text bubble
        random_conv = ConversationBubbles(self.rect.topright,self.game_objects, text)
        self.game_objects.cosmetics.add(random_conv)

    def buisness(self):#enters after conversation
        pass