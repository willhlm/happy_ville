from game_states import Gameplay
from entities import Spawneffect, Lighitning, Reindeer, Cultist_warrior, Cultist_rogue
import read_files
import animation
import particles

#file based
class Cutscene_file():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.animation = animation.Animation(self)
        self.sprites = {'idle': read_files.load_sprites_list('cutscene/'+type(self).__name__.lower(), game_objects)}
        self.image = self.sprites['idle'][0]

    def update(self):
        self.animation.update()

    def render(self):
        self.game_objects.game.display.render(self.image,self.game_objects.game.screen)

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        input.processed()

class Rhoutta_encounter_defeat(Cutscene_file):#play the first cutscene encountering rhoutta
    def __init__(self,objects):
        super().__init__(objects)
        self.game_objects.load_map(None, 'wakeup_forest_1', fade = False)#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.game_objects.state_manager.exit_state()
        self.game_objects.state_manager.enter_state('Title_screen')

#engine based
class Cutscene_engine(Gameplay):#cut scenens that is based on game engien
    def __init__(self,game):
        super().__init__(game)
        self.timer = 0
        self.pos = [-self.game.window_size[1],self.game.window_size[1]]
        self.const = [0.8,0.8]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.rect1 = game.display.make_layer(self.game.window_size)#TODO
        self.rect2 = game.display.make_layer(self.game.window_size)#TODO

        self.rect2.clear(0,0,0,255)
        self.rect1.clear(0,0,0,255)

    def render(self):
        super().render()
        self.cinematic()

    def handle_movement(self):
        pass

    def cinematic(self):#black box stuff
        self.pos[0] += self.game.dt#the upper balck box
        self.pos[1] -= self.game.dt#the lower balck box

        self.pos[0] = min(-self.game.window_size[1]*self.const[0], self.pos[0])
        self.pos[1] = max(self.game.window_size[1]*self.const[1], self.pos[1])

        self.game.display.render(self.rect1.texture, self.game.screen, position = [0,self.pos[0]])
        self.game.display.render(self.rect2.texture, self.game.screen, position = [0,self.pos[1]])

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] == 'a':
                self.press = True

class New_game(Cutscene_engine):#first screen to be played when starying a new game -> needs to be called after that the map has loaded
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.camera_manager.set_camera('New_game')#when starting a new game, should be a cutscene
        self.camera_stops = []#temporary remove the came stops
        for camera_stop in self.game.game_objects.camera_blocks:
            self.camera_stops.append(camera_stop)
        self.game.game_objects.camera_blocks.empty()

    def cinematic(self):
        pass

    def update(self):
        super().update()
        self.timer += self.game.dt
        if self.timer > 500:
            self.game.state_manager.exit_state()

    def on_exit(self):
        for camera_stop in self.camera_stops:
            self.game.game_objects.camera_blocks.add(camera_stop)
        self.game.game_objects.camera_manager.camera.exit_state()
        super().on_exit()

class Title_screen(Cutscene_engine):#screen played after waking up from boss dream
    def __init__(self,game):
        super().__init__(game)
        self.title_name = self.game.game_objects.font.render(text = 'Happy Ville')
        self.text1 = self.game.game_objects.font.render(text = 'A game by Hjortron games')
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.cosmetics.empty()

    def update(self):
        super().update()
        self.timer += self.game.dt

    def render(self):
        super().render()
        if self.timer>250:
            self.game.display.render(self.title_name,self.game.screen,position = (190,150))

        if self.timer>500:
            self.game.display.render(self.text1,self.game.screen,position = (190,170))

        if self.timer >700:
            self.game.game_objects.player.acceleration[0] *= 2#bacl to normal speed
            self.game.state_manager.exit_state()

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] == 'a':
                self.press = True

        if event[-1]=='right' or event[-1]=='left' or event[-1] == None or event[-1]=='down' or event[-1]=='up':#left stick and arrow keys
            if event[2]['l_stick'][0] > 0: return#can only go left
            event[2]['l_stick'][0] *= 0.5#half the speed
            self.game.game_objects.player.currentstate.handle_movement(event)

class Deer_encounter(Cutscene_engine):#first deer encounter in light forest by waterfall
    def __init__(self,game):
        super().__init__(game)
        pos = [2992, 848]
        self.entity = Reindeer(pos, game.game_objects)
        game.game_objects.enemies.add(self.entity)
        self.game.game_objects.camera_manager.set_camera('Deer_encounter')
        self.game.game_objects.player.currentstate.enter_state('Run_pre')#should only enter these states once
        self.stage = 0

    def update(self):#write how you want things to act
        super().update()
        self.timer += self.game.dt
        if self.stage == 0:

            if self.timer < 50:
                self.game.game_objects.player.velocity[0] = 4

            elif self.timer > 50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0
                self.stage  = 1
                
        elif self.stage ==1:
            if self.timer > 200:
                self.entity.currentstate.queue_task(task = 'walk', animation = 'walk_nice')   
                self.entity.currentstate.queue_task(task = 'idle')
                self.entity.currentstate.start_next_task()
                
                self.entity.velocity[0] = 5      
                self.entity.dir[0] *= -1
                self.stage = 2

        elif self.stage ==2:
            if self.timer > 200:                   
                self.entity.velocity[0] = 5

        if self.timer>300:
            self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.game_objects.camera_manager.camera.exit_state()
        self.entity.kill()
        self.game.game_objects.world_state.cutscene_complete('deer_encounter')
        super().on_exit()

class Boss_deer_encounter(Cutscene_engine):#boss fight cutscene
    def __init__(self, game):
        super().__init__(game)
        pos = [5888, 600]
        self.entity = Reindeer(pos, game.game_objects)
        game.game_objects.enemies.add(self.entity)
        self.entity.dir[0] = -1

        self.game.game_objects.camera_manager.set_camera('Deer_encounter')
        self.stage = 0
        
        self.game.game_objects.player.shader_state.handle_input('idle')        
        self.game.game_objects.player.acceleration[0]  = 1#start walking        

    def update(self):#write how you want the player/group to act
        super().update()
        self.timer += self.game.dt
        if self.stage == 0:
            if self.timer > 120:
                self.stage = 1
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0

        elif self.stage==1:#transform
            if self.timer > 200:
                self.entity.currentstate.queue_task(task = 'transform')
                self.entity.currentstate.queue_task(task = 'idle', animation = 'idle')
                self.entity.currentstate.start_next_task()
                self.game.game_objects.player.velocity[0] = -20
                self.stage = 2

        elif self.stage==2:#roar
            if self.timer > 300:
                self.entity.currentstate.queue_task(task = 'roar_pre')
                self.entity.currentstate.queue_task(task = 'roar_main')
                self.entity.currentstate.queue_task(task = 'roar_post')
                self.entity.currentstate.queue_task(task = 'idle', animation = 'idle')                
                self.entity.currentstate.start_next_task()
                self.stage = 3

        elif self.stage==3:
            if self.timer > 600:
                self.game.game_objects.camera_manager.camera.exit_state()#exsiting deer encounter camera
                self.entity.currentstate.queue_task(task = 'think')
                self.entity.currentstate.start_next_task()
                self.game.state_manager.exit_state()                

class Defeated_boss(Cutscene_engine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self.step1 = False
        self.const = [0.5,0.5]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.timer < 75:
            self.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.game.game_objects.player.velocity[1] = -1#compensates for gravity, levitates
            self.step1 = True

        if self.timer > 250:
            self.game.game_objects.player.velocity[1] = 2#go down again
            if self.game.game_objects.player.collision_types['bottom']:
                self.game.state_manager.exit_state()

    def render(self):
        super().render()
        if self.step1:
            particle = getattr(particles, 'Spark')(self.game.game_objects.player.rect.center, self.game.game_objects, distance = 400, lifetime = 60, vel = {'linear':[7,13]}, dir = 'isotropic', scale = 1, colour = [255,255,255,255])
            self.game.game_objects.cosmetics.add(particle)

            self.game.game_objects.cosmetics.draw(self.game.game_objects.game.screen)
            self.game.game_objects.players.draw(self.game.game_objects.game.screen)

class Death(Cutscene_engine):#when aila dies
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0

    def update(self):
        super().update()
        #if self.game.state_manager.state_stack[-1] != self: return#needed
        self.timer += self.game.dt
        if self.stage == 0:

            if self.timer > 120:
                self.state1()

        elif self.stage == 1:
                #spawn effect
                pos = (0,0)#
                offset = 100#depends on the effect animation
                self.spawneffect = entities.Spawneffect(pos,self.game.game_objects)
                self.spawneffect.rect.midbottom=self.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom += offset
                self.game.game_objects.cosmetics.add(self.spawneffect)
                self.stage = 2

        elif self.stage == 2:
            if self.spawneffect.finish:#when the cosmetic effetc finishes
                self.game.game_objects.player.currentstate.enter_state('Spawn_main')
                self.game.state_manager.exit_state()

    def state1(self):
        if self.game.game_objects.player.backpack.map.spawn_point.get('bone', False):#respawn by bone
            map = self.game.game_objects.player.backpack.map.spawn_point['bone']['map']
            point = self.game.game_objects.player.backpack.map.spawn_point['bone']['point']
            del self.game.game_objects.player.backpack.map.spawn_point['bone']
        else:#normal resawn
            map = self.game.game_objects.player.backpack.map.spawn_point['map']
            point =  self.game.game_objects.player.backpack.map.spawn_point['point']
        self.game.game_objects.load_map(self, map, point)
        self.stage = 1

    def handle_events(self,input):
        input.processed()

    def cinematic(self):
        pass

class Cultist_encounter(Cutscene_engine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.player.death_state.handle_input('cultist_encounter')
        self.game.game_objects.quests_events.initiate_quest('cultist_encounter', kill = 2)

        pos = [1420, 500]
        self.entity1 = Cultist_warrior(pos, game.game_objects)
        self.game.game_objects.enemies.add(self.entity1)
        
        self.stage = 0
        self.game.game_objects.camera_manager.set_camera('Cultist_encounter')
        self.game.game_objects.player.currentstate.enter_state('Run_pre')#should only enter these states once

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.stage==0:#encounter Cultist_warrior
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=-4
                self.game.game_objects.player.acceleration[0]=1

            elif self.timer > 50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                #self.game.game_objects.player.velocity[0]=0
                self.game.game_objects.player.acceleration[0] = 0

                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:#sapawn cultist_rogue

                spawn_pos = self.game.game_objects.player.rect.topright  
                self.entity2 = Cultist_rogue(spawn_pos, self.game.game_objects)                               
                self.entity2.dir[0] = -1
                self.entity2.currentstate.enter_state('Ambush_pre')    
                self.game.game_objects.enemies.add(self.entity2)

                self.stage=2
                self.timer=0

        elif self.stage==2:
            if self.timer>100:
                self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.game_objects.camera_manager.camera.exit_state()
        super().on_exit()

class Rhoutta_encounter(Gameplay):#called from trigger before first rhoutta: shuold spawn lightning and a gap spawns, or something -> TODO make a cutsene
    def __init__(self, game):
        super().__init__(game)
        spawn_pos = (1520-40,416-336)#topleft position in tiled - 40 to spawn it behind aila
        lightning = entities.Lighitning(spawn_pos,self.game.game_objects, parallax = [1,1], size = [64,336])
        effect = entities.Spawneffect(spawn_pos,self.game.game_objects)
        effect.rect.midbottom = lightning.rect.midbottom
        self.game.game_objects.interactables.add(lightning)
        self.game.game_objects.cosmetics.add(effect)
        self.game.game_objects.weather.flash()

class Butterfly_encounter(Cutscene_engine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0
        self.game.game_objects.signals.emit('who_is_cocoon', callback = self.set_entity) 
        self.const[1] = 0.9

    def set_entity(self, entity):#the entity to control, set through signals
        self.entity = entity

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.stage ==0:#approch
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=4
                self.game.game_objects.player.acceleration[0] = 1

            elif self.timer > 150:#stay
                self.game.game_objects.player.currentstate.enter_state('Idle_main')
                self.game.game_objects.player.acceleration[0]=0
                self.stage = 1

        elif self.stage == 1:#aggro

            if self.timer > 200:
                self.game.game_objects.camera_manager.camera_shake(duration = 200)
                self.stage = 2

        elif self.stage == 2:#spawn
            self.entity.particle_release()
            if self.timer > 400:
                self.game_objects.quests_events.initiate_quest('butterfly_encounter')
                self.game.state_manager.exit_state()
