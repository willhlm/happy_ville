import sys, random
import Entities, platforms

class Quests_events():#quest and event handlere
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_quests = {}#quests the player has picked up. the object is only initiated once when picking it up
        self.active_events = {}#events that occur during gameplay. New object is always initiated.

    def initiate_quest(self, quest, **kwarg):#if a quest flag is set in world_state, this should not be called
        if not self.active_quests.get(quest, False):#if it is the first time getting the quest
            self.active_quests[quest] = getattr(sys.modules[__name__], quest.capitalize())(self.game_objects, **kwarg)#make a class based on the name of the newstate: need to import sys
        self.active_quests[quest].initiate_quest()#if it alraedy exits, re initate it
       
    def initiate_event(self, event, **kwarg):#events e.g. encounters: probably don't need to save all of them?
        self.active_events[event] = getattr(sys.modules[__name__], event.capitalize())(self.game_objects, **kwarg)#make a class based on the name of the newstate: need to import sys

class Quest_event():
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def initiate_quest(self):
        pass

    def complete(self):
        pass

    def fail(self):
        pass        

#encounters
class Butterfly_encounter(Quest_event):#called from cutscene if aggro path is chosen: and should be called if cocoon gets hurt
    def __init__(self, game_objects):
        super().__init__(game_objects)
        spawn_pos = self.game_objects.map.references['cocoon_boss'].rect.topleft
        self.game_objects.weather.flash()
        butterfly = Entities.Butterfly(spawn_pos, self.game.game_objects, self)
        self.game_objects.enemies.add(butterfly)
        self.game_objects.map.references['cocoon_boss'].currentstate.handle_input('Hurt')
        spawn_pos = [2576, 1320]
        self.gate = Entities.Lighitning(spawn_pos,self.game.game_objects,[1,1],[32,96])
        self.game_objects.interactables.add(self.gate)
        butterfly.AI.activate()

    def incrase_kill(self):#called when butterfly is dead
        self.complete()

    def complete(self):
        self.game_objects.world_state.cutscenes_complete[type(self).__name__.lower()] = True
        self.game_objects.world_state.events[type(self).__name__.lower()] = True          
        self.gate.currentstate.handle_input('Transform')

class Cultist_encounter(Quest_event):#called from cutscene when meeting the cultist across the bridgr the first time: initiated from cutscene
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.kill = kwarg['kill']
        self.gate = platforms.Gate((self.game_objects.camera.scroll[0] - 250,self.game_objects.camera.scroll[1] + 100), self.game_objects, erect = True)#added to group in cutscene

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.kill -= 1
        if self.kill <= 0:#both cultist have died
            self.complete()
    
    def complete(self):
        self.gate.currentstate.handle_input('Transform')
        self.game_objects.player.death_state.handle_input('idle')
        self.game_objects.world_state.cutscenes_complete[type(self).__name__.lower()] = True
        self.game_objects.world_state.events[type(self).__name__.lower()] = True  

class Acid_escape(Quest_event):#golden fields
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        pos = [-2000 + game_objects.camera.scroll[0],game_objects.game.window_size[1] + game_objects.camera.scroll[1]]
        size = [5000, game_objects.game.window_size[1]]
        self.acid = Entities.TwoD_liquid(pos, game_objects, size, vertical = True)
        game_objects.interactables_fg.add(self.acid)

    def complete(self):
        self.game_objects.world_state.events[type(self).__name__.lower()] = True  
        self.acid.kill()

#quests
class Lumberjack_omamori(Quest_event):#called from monument, #TODO need to make so that this omamori cannot be eqquiped while this quest is runing
    def __init__(self, game_objects, item = None):
        super().__init__(game_objects)
        self.description = 'bring back the omamori to lumberjack within a given time'        
        self.time = 9000#time to compplete        
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

class Fragile_butterfly(Quest_event):#TODO
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.description = 'could you deliver my pixie dust to my love. Do not take damage.'    
   
    def fail(self):#should be called when taking dmg
        self.game_objects.world_state.quests['fragile_butterfly'] = False    

    def initiate_quest(self):#called to initiate
        self.game_objects.world_state.quests['fragile_butterfly'] = True   

    def complete(self):#called when delivered
        self.game_objects.world_state.quests['fragile_butterfly'] = True

#rooms from monuments       
class Ball_room(Quest_event):#the room with ball in light forest cavee
    def __init__(self, game_objects, **kwarg):  
        super().__init__(game_objects)   
        self.description = 'destroy all balls within a given time'   
        self.monument = kwarg['monument']        
        self.time = 600        
    
    def initiate_quest(self):#called when interact with monument      
        self.timer = Entities.Timer_display(self, self.time)
        self.game_objects.cosmetics.add(self.timer)  
        pos = self.monument.rect.center
        self.number = 5#number of balls        
        self.spawn_balls(pos)
        self.get_gates()        
    
    def spawn_balls(self, pos):
        for i in range(0, self.number):
            new_ball = Entities.Bouncy_balls((pos[0],pos[1] - 20), self.game_objects, quest = self, lifetime = self.time)         
            self.game_objects.eprojectiles.add(new_ball)   

    def get_gates(self):#trap aila
        self.gates = {}
        for gate in self.game_objects.map.references['gate']:
            if gate.ID_key == 'ball_room1':#these strings are specified in tiled
                gate.currentstate.handle_input('Transform')       
                self.gates['1'] = gate
            elif gate.ID_key == 'ball_room':#these strings are specified in tiled
                self.gates['2'] = gate#this one is already erect

    def time_out(self):#when timer runs out
        self.failiure()

    def failiure(self):
        self.timer.kill()
        self.gates['1'].currentstate.handle_input('Transform')   
        self.game_objects.world_state.quests[type(self).__name__.lower()] = False                
        self.monument.reset()

    def complete(self):
        self.timer.kill()
        self.game_objects.world_state.quests[type(self).__name__.lower()] = True        
        for key in self.gates.keys():#open the gates
            self.gates[key].currentstate.handle_input('Transform')     

    def increase_kill(self):#called wgeb ball is destroyed
        self.number -= 1
        if self.number <= 0:
            self.complete()             

class Portal_rooms(Quest_event):#challanges with portals
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.monument = kwarg['monument']   
    
    def initiate_room(self):#portal calls it after growing
        pass        

    def initiate_quest(self):
        pos = self.monument.rect.center                        
        self.portal = Entities.Portal([pos[0] + 100, pos[1] - 20], self.game_objects, state = self)        
        self.game_objects.special_shaders.add(self.portal) 

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated        
            self.complete()#if there was a gate, we can open it    
    
    def complete(self):
        self.portal.currentstate.handle_input('shrink')        
        self.game_objects.world_state.quests[type(self).__name__.lower()] = True        
        for gate in self.gates:
            gate.kill()            

    def put_gate(self):        
        pos = [self.portal.rect.topleft, self.portal.rect.topright]
        self.gates = []
        for num in range(0,2):
            self.gates.append(Entities.Bubble_gate(pos[num],self.game_objects,[100,340]))
            self.game_objects.interactables.add(self.gates[-1])                              

class Room_0(Portal_rooms):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)

    def initiate_room(self):#specific for each room
        self.put_gate()
        self.number = 1
        for number in range(0, self.number):
            pos = [600 +  random.randint(-100, 100), 300 +  random.randint(-100, 100)]
            enemy = Entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)          
        
