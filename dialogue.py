class Dialogue():
    def __init__(self,entity):
        self.entity = entity
        self.conv_index = 0
        self.load_conversation()

    def load_conversation(self):
        self.conversation = Read_files.read_json("Text/NPC/" + self.entity.name + ".json")

    def reset_conv_index(self):
        self.conv_index = 0

    def increase_conv_index(self):
        self.conv_index += 1

    def get_dialogue(self):
        #check events according yo priority
        for event in self.entity.priority:
            if self.entity.game_objects.world_state[event]:#if the priority event has occured
                self.entity.priority.remove(event)
                return self.entity.conversation[event]

        for event in self.entity.event:
            if self.entity.game_objects.world_state[event]:#if the priority event has occured
                self.entity.event.remove(event)
                return self.entity.conversation[event]


        state = 'state_' + str(self.entity.game_objects.world_state.progress)
        return self.conversation[state][str(self.conv_index)]
