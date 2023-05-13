import Read_files

class Dialogue():#handles dialoage and what to say
    def __init__(self,entity):
        self.entity = entity
        self.conv_index = 0
        self.conversation = Read_files.read_json("Text/NPC/" + self.entity.name + ".json")

    def reset_conv_index(self):
        self.conv_index = 0

    def increase_conv_index(self):
        self.conv_index += 1

    def finish(self,event):#is the conversation finished?
        if self.conv_index >= len(self.conversation[event]):
            self.reset_conv_index()#should it reset or stay at the last? depends on conversation type?
            return True

    def get_conversation(self):
        #decide priority
        for event in self.entity.priority:#check events according yo priority
            if self.entity.game_objects.world_state.events[event]:#if the priority event has occured
                if self.finish(event):
                    self.entity.priority.remove(event)
                    return None
                return self.conversation[event][str(self.conv_index)]

        for event in self.entity.event:
            if self.entity.game_objects.world_state.events[event]:#if the event has occured
                if self.finish(event):
                    self.entity.event.remove(event)
                    return None
                return self.conversation[event]

        #if no priority events have happened, return normal conversation
        event = 'state_' + str(self.entity.game_objects.world_state.progress)
        if self.finish(event):
            return None
        return self.conversation[event][str(self.conv_index)]
