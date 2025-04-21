import read_files, random, math
from entities_core import Staticentity

class Conversation():
    def __init__(self,entity):
        self.entity = entity    
        self.conv_index = 0

    def reset_conv_index(self):
        self.conv_index = 0

    def increase_conv_index(self):
        self.conv_index += 1

    def finish(self,event):#is the conversation finished?
        if self.conv_index >= len(self.dialoages['conversation'][event]):
            self.reset_conv_index()#should it reset or stay at the last? depends on conversation type?
            return True

class Dialogue(Conversation):#handles dialoage and what to say for NPC
    def __init__(self,entity):
        super().__init__(entity)
        self.dialoages = {'conversation': read_files.read_json("text/NPC/conversation/" + self.entity.name + ".json"), 'comment': read_files.read_json("text/NPC/comment/" + self.entity.name + ".json") }

    def get_comment(self):#random text bubbles
        event = 'state_' + str(self.entity.game_objects.world_state.progress)
        options = len(self.dialoages['comment'][event].keys()) - 1
        value = random.randint(0,options)
        return self.dialoages['comment'][event][str(value)]        

    def get_conversation(self):#quest stuff first, then priority evens, and then normal events followed by notmal conversation
        #decide priority        
        for event in self.entity.quest:#check events according yo priority
            if self.entity.game_objects.world_state.quests.get(event, False):#if the priority event has occured
                if self.finish(event):
                    self.entity.quest.remove(event)
                    return None
                return self.dialoages['conversation'][event][str(self.conv_index)]

        for event in self.entity.priority:#check events according yo priority
            if self.entity.game_objects.world_state.events.get(event, False):#if the priority event has occured
                if self.finish(event):
                    self.entity.priority.remove(event)
                    return None
                return self.dialoages['conversation'][event][str(self.conv_index)]

        for event in self.entity.event:
            if self.entity.game_objects.world_state.events.get(event, False):#if the event has occured
                if self.finish(event):
                    self.entity.event.remove(event)
                    return None
                return self.dialoages['conversation'][event][str(self.conv_index)] 

        #if no priority events have happened, return normal conversation
        event = 'state_' + str(self.entity.game_objects.world_state.progress)
        if self.finish(event):
            return None
        return self.dialoages['conversation'][event][str(self.conv_index)]

class Dialogue_interactable(Conversation):#interactables
    def __init__(self, entity, name):
        super().__init__(entity)
        self.dialoages = {'conversation':read_files.read_json("text/interactables/" + name + ".json")}

    def get_conversation(self):#quest stuff first, then priority evens, and then normal events followed by notmal conversation        
        event = 'state_0'
        if self.finish(event):
            return None
        return self.dialoages['conversation'][event][str(self.conv_index)]

class Conversation_bubbles(Staticentity):
    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)
        self.render_text(text)

        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        Conversation_bubbles.layer = game_objects.game.display.make_layer(size)
        Conversation_bubbles.bg = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self):
        self.time += self.game_objects.game.dt * 0.1
        self.update_vel()
        self.update_pos()
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.game_objects.game.dt,self.true_pos[1] + self.velocity[1]*self.game_objects.game.dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)

    def render_text(self, text):
        texture = self.game_objects.font.render(text = text)
        self.game_objects.game.display.render(self.bg, self.layer)#shader render
        self.game_objects.game.display.render(texture, self.layer, position = [10, self.rect[3]])#shader render
        self.image = self.layer.texture
        texture.release()        