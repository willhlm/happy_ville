from gameplay.entities.npc.base.npc import NPC

from gameplay.entities.states import states_shader_guide

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        if self.game_objects.world_state.state.get('reindeer', False):#if player has deafated the reindeer
            if not self.game_objects.player.states['Wall_glide']:#if player doesn't have wall yet (so it only enters once)
                self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game.game_objects.player.sprites[Wall_glide][0].copy())
                self.game_objects.player.states['Wall_glide'] = True

class Guide(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.shader_state = states_shader_guide.Idle(self)
        self.layer1 = self.game_objects.game.display.make_layer(self.image.size)#make a layer ("surface")TODO

    def update(self, dt):
        super().update(dt)
        self.shader_state.update(dt)#goes between idle and teleport

    def buisness(self):#enters after conversation
        self.shader_state = states_shader_guide.Teleport(self)
        for i in range(0, 10):#should maybe be the number of abilites Aila can aquire?
            particle = getattr(particles, 'Circle')(self.hitbox.center, self.game_objects, distance=0, lifetime = -1, vel = {'linear':[7,15]}, dir='isotropic', scale=5, colour=[100,200,255,255], state = 'Circle_converge',gradient = 1)
            light = self.game_objects.lights.add_light(particle, colour = [100/255,200/255,255/255,255/255], radius = 20)
            particle.light = light#add light reference
            self.game_objects.cosmetics.add(particle)

    def give_light(self):#called when teleport shader is finished
        self.game_objects.lights.add_light(self.game_objects.player, colour = [200/255,200/255,200/255,200/255])
        self.game_objects.world_state.update_event('guide')

    def draw(self, target):#called in group
        self.shader_state.draw()
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

class Sahkar(NPC):#deer handler
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Busty_baker(NPC):#bartender
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_droplet':1}#itam+price
        text = self.dialogue.get_comment()
        self.random_conversation(text)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Vendor', category = 'game_states_facilities', npc = self)

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Smith', category = 'game_states_facilities', npc = self)

class MrMine(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = ['reindeer']#priority events to say
        self.event = []#normal events to say
        self.quest = []#quest stuff to say

class MrCarpenter(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = []#priority events to say
        self.event = []#normal events to say
        self.quest = []#quest stuff to say

class MrBanks(NPC):#bank
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Bank', category = 'game_states_facilities', npc = self)

class MsButterfly(NPC):#lumber jack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest('fragile_butterfly')
        self.game_objects.player.inventory['pixie dust'] = 1

class MrWood(NPC):#lumber jack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = []#priority events to say
        self.event = []#normal events to say
        self.quest = ['lumberjack_radna']#quest stuff to say

    def interact(self):#when plater press t
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)
        if self.game_objects.world_state.quests.get('lumberjack_radna', False):#if the quest is running
            self.game_objects.quests_events.active_quests['lumberjack_radna'].complete()