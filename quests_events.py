import sys, random
import entities, platforms

class Quests_events():#quest and event handlere
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_quests = {}#quests the player has picked up. the object is only initiated when picking it up
        self.active_events = {}#events that occur during gameplay. New object is always initiated.

    def initiate_quest(self, quest, **kwarg):
        if not self.active_quests.get(quest, False):#if it is the first time getting the quest
            self.active_quests[quest] = getattr(sys.modules[__name__], quest.capitalize())(self.game_objects, **kwarg)#make a class based on the name of the newstate: need to import sys
        self.active_quests[quest].initiate_quest()#if it alraedy exits, re initate it
       
    def initiate_event(self, event, **kwarg):#events e.g. encounters: probably don't need to save all of them?
        self.active_events[event] = getattr(sys.modules[__name__], event.capitalize())(self.game_objects, **kwarg)#make a class based on the name of the newstate: need to import sys        

class Tasks():#events and quests
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def initiate_quest(self):
        pass

    def complete(self):
        pass

    def fail(self):
        pass        

#encounters
class Butterfly_encounter(Tasks):#called from cutscene if aggro path is chosen: and should be called if cocoon gets hurt
    def __init__(self, game_objects):
        super().__init__(game_objects)
        spawn_pos = self.game_objects.map.references['cocoon_boss'].rect.topleft
        self.game_objects.weather.flash()
        butterfly = entities.Butterfly(spawn_pos, self.game_objects)
        self.game_objects.enemies.add(butterfly)
        self.game_objects.map.references['cocoon_boss'].currentstate.handle_input('Hurt')
        spawn_pos = [2576, 1320]
        self.gate = entities.Lighitning(spawn_pos,self.game_objects,[1,1],[32,96])
        self.game_objects.interactables.add(self.gate)
        butterfly.AI.activate()

        self.game_objects.signals.subscribe('butterfly_killed', self.complete)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def complete(self):#called when butterfly is dead
        self.game_objects.world_state.cutscenes_complete[type(self).__name__.lower()] = True
        self.game_objects.world_state.events[type(self).__name__.lower()] = True          
        self.gate.currentstate.handle_input('Transform')
        self.cleanup()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('butterfly_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

class Cultist_encounter(Tasks):#called from cutscene when meeting the cultist across the bridgr the first time: initiated from cutscene
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.kill = kwarg['kill']
        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)
        #self.gate = platforms.Gate((self.game_objects.camera_manager.camera.scroll[0] - 250,self.game_objects.camera_manager.camera.scroll[1] + 100), self.game_objects, erect = True)#added to group in cutscene

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.kill -= 1
        if self.kill <= 0:#both cultist have died
            self.complete()            

    def handle_player_death(self):# Called when the player dies
        self.cleanup()

    def complete(self):
        #self.gate.currentstate.handle_input('Transform')
        self.game_objects.player.death_state.handle_input('idle')
        self.game_objects.world_state.cutscenes_complete[type(self).__name__.lower()] = True
        self.game_objects.world_state.events[type(self).__name__.lower()] = True  
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

class Acid_escape(Tasks):#called in golden fields "last room"
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        pos = [-2000 + game_objects.camera_manager.camera.scroll[0],game_objects.game.window_size[1] + game_objects.camera_manager.camera.scroll[1]]
        size = [5000, game_objects.game.window_size[1]]
        self.acid = entities.TwoD_liquid(pos, game_objects, size, vertical = True)
        game_objects.interactables_fg.add(self.acid)

    def complete(self):
        self.game_objects.world_state.events[type(self).__name__.lower()] = True  
        self.acid.kill()

class Golden_fields_encounter_1(Tasks):#called from golden fields room event_trigger
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.get_gates()
        self.spawn_enemy()
        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def spawn_enemy(self):
        self.number = 1
        for number in range(0, self.number):            
            pos = [1728 +  random.randint(-10, 10), 1200 +  random.randint(-10, 10)]
            enemy = entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)              

    def get_gates(self):#trap aila
        self.gates = {}
        for gate in self.game_objects.map.references['gate']:
            if gate.ID_key == 'golden_fields_encounter_1_1':#these strings are specified in tiled
                self.gates['1'] = gate
                self.gates['1'].currentstate.handle_input('Transform')
            elif gate.ID_key == 'golden_fields_encounter_1_2':#these strings are specified in tiled
                self.gates['2'] = gate#this one is already erect     

    def handle_player_death(self):# Called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

    def incrase_kill(self):#called when enemy is called
        self.number -= 1
        if self.number == 0:#all enemies eleminated        
            self.complete()  

    def complete(self):
        for key in self.gates.keys():
            self.gates[key].currentstate.handle_input('Transform')
        self.game_objects.world_state.events[type(self).__name__.lower()] = True 
        self.cleanup()    

#quests
class Lumberjack_radna(Tasks):#called from monument, #TODO need to make so that this radna cannot be eqquiped while this quest is runing
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.description = 'bring back the radna to lumberjack within a given time'        
        self.time = 9000#time to compplete        
        self.radna = kwarg['item']

    def time_out(self):#called when timer_display runs out   
        del self.game_objects.player.backpack.necklace.inventory[self.radna] #remove the radna    
        self.game_objects.world_state.quests['lumberjack_radna'] = False        

    def initiate_quest(self):#called when radna is picked up 
        self.game_objects.world_state.quests['lumberjack_radna'] = True        
        self.timer = entities.Timer_display(self, self.time)
        self.game_objects.cosmetics_no_clear.add(self.timer)       
        
    def complete(self):#called when talking to lumberjack within the timer limit        
        self.timer.kill()                         

class Fragile_butterfly(Tasks):#TODO -> light forest cave
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.description = 'could you deliver my pixie dust to my love. Do not take damage.'    
   
    def fail(self):#should be called when taking dmg
        self.game_objects.world_state.quests['fragile_butterfly'] = False    

    def initiate_quest(self):#called to initiate
        self.game_objects.world_state.quests['fragile_butterfly'] = True   

    def complete(self):#called when delivered
        self.game_objects.world_state.quests['fragile_butterfly'] = True

class Larv_party(Tasks):#william's larv room
    def __init__(self, game_objects):
        super().__init__(game_objects)    
        self.number = 20#number of larvs on the map

    def incrase_kill(self):#called when larv_jr is killed: signal
        self.number -= 1
        if self.number < 0:
            self.complete()

    def initiate_quest(self):
        self.running = True#a flag to check if the quest is running: needed so that collision only enters here once
        self.game_objects.signals.subscribe('larv_jr_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)        
    
    def pause_quest(self):
        self.cleanup()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):  
        self.running = False      
        self.game_objects.signals.unsubscribe('larv_jr_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

    def complete(self):
        self.game_objects.world_state.quests[type(self).__name__.lower()] = True  
        self.cleanup()   

#rooms from monuments       
class Ball_room(Tasks):#the room with ball in light forest cavee
    def __init__(self, game_objects, **kwarg):  
        super().__init__(game_objects)   
        self.description = 'destroy all balls within a given time'   
        self.monument = kwarg['monument']        
        self.time = 600  
        
    def initiate_quest(self):#called when interact with monument      
        self.timer = entities.Timer_display(self, self.time)
        self.game_objects.cosmetics.add(self.timer)  
        pos = self.monument.rect.center
        self.number = 5#number of balls        
        self.spawn_balls(pos)
        self.get_gates()       

        self.game_objects.signals.subscribe('ball_killed', self.increase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)         
    
    def spawn_balls(self, pos):
        for i in range(0, self.number):
            new_ball = entities.Bouncy_balls((pos[0],pos[1] - 20), self.game_objects, lifetime = self.time)         
            self.game_objects.eprojectiles.add(new_ball)   

    def get_gates(self):#trap aila
        self.gates = {}
        for gate in self.game_objects.map.references['gate']:
            if gate.ID_key == 'ball_room_1':#these strings are specified in tiled
                gate.currentstate.handle_input('Transform')       
                self.gates['1'] = gate
            elif gate.ID_key == 'ball_room_2':#these strings are specified in tiled
                self.gates['2'] = gate#this one is already erect

    def time_out(self):#when timer runs out: fail
        self.timer.kill()
        self.gates['1'].currentstate.handle_input('Transform')   
        self.game_objects.world_state.quests[type(self).__name__.lower()] = False                
        self.monument.reset()
        self.cleanup()

    def increase_kill(self):#called wgeb ball is destroyed
        self.number -= 1
        if self.number <= 0:
            self.complete()  

    def complete(self):
        self.timer.kill()
        self.cleanup()        
        self.game_objects.world_state.quests[type(self).__name__.lower()] = True        
        for key in self.gates.keys():#open the gates
            self.gates[key].currentstate.handle_input('Transform')     

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self): 
        self.game_objects.signals.unsubscribe('ball_killed', self.increase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

class Portal_rooms(Tasks):#challanges with portals
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.monument = kwarg['monument']   
    
    def initiate_room(self):#portal calls it after growing
        pass        

    def initiate_quest(self):
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)           
        pos = self.monument.rect.center                        
        self.portal = entities.Portal([pos[0] + 100, pos[1] - 20], self.game_objects, state = self)        
        self.game_objects.special_shaders.add(self.portal) 

    def put_gate(self):        
        pos = [self.portal.rect.topleft, self.portal.rect.topright]
        self.gates = []
        for num in range(0,2):
            self.gates.append(entities.Bubble_gate(pos[num],self.game_objects,[100,340]))
            self.game_objects.interactables.add(self.gates[-1])          

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated        
            self.complete()#if there was a gate, we can open it    
    
    def complete(self):
        self.cleanup()
        self.portal.currentstate.handle_input('shrink')        
        self.game_objects.world_state.quests[type(self).__name__.lower()] = True        
        for gate in self.gates:
            gate.kill()                                

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self): 
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)           

class Room_0(Tasks):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)     

    def initiate_room(self):#specific for each room
        self.put_gate()
        self.number = 1
        for number in range(0, self.number):
            pos = [600 +  random.randint(-100, 100), 300 +  random.randint(-100, 100)]
            enemy = entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)     

        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)                         
        
    def cleanup(self): 
        super().cleanup()
        self.game_objects.signals.unsubscribe('cultist_killed', self.increase_kill)
