import sys
import Entities

class Quest():#quest handlere
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_quests = {}#quests the player has picked up

    def initiate_quest(self, quest, **kwarg):
        if not self.active_quests.get(quest, False):#if it is the first time getting the quest
            self.active_quests[quest] = getattr(sys.modules[__name__], quest.capitalize())(self.game_objects, **kwarg)#make a class based on the name of the newstate: need to import sys
        else:#otherwise, just start it again
            self.active_quests[quest].initiate_quest()
        
class Lumberjack_omamori():#TODO need to make so that this omamori cannot be eqquiped while this quest is runing
    def __init__(self, game_objects, item):
        self.game_objects = game_objects
        self.description = 'bring back the omamori to lumberjack within a given time'        
        self.time = 9000#time to compplete
        self.initiate_quest()
        self.omamori = item

    def time_out(self):#when time runs out   
        name = type(self.omamori).__name__
        del self.game_objects.player.omamoris.inventory[name] #remove the omamori    
        self.game_objects.world_state.quests['lumberjack_omamori'] = False        

    def initiate_quest(self):#called when omamori is picked up        
        self.game_objects.world_state.quests['lumberjack_omamori'] = True        
        self.timer = Entities.Timer_display(self, self.time)
        self.game_objects.cosmetics_no_clear.add(self.timer)        
        
    def complete(self):#called when talking to lumberjack within the timer limit        
        self.timer.kill()
        

        
        
