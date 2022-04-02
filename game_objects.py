import pygame, sys
import Read_files
import Engine
import Entities
import Level
import map_loader
import BG
import sound
import states

class Game_Objects():

    def __init__(self, game):

        self.game = game
        self.map_state = Read_files.read_json("map_state.json") #check this file for structure of object
        self.sound = sound.Sound()
        self.collisions = Engine.Collisions()
        self.FADEIN = False
        self.BLACKEDOUT = False
        self.fadein_length = 20
        self.blackedout_length = 40
        self.fade_count = 0
        self.create_groups()

    def create_groups(self):

        #define all sprite groups
        self.enemies = Entities.ExtendedGroup()# pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.platforms_ramps = pygame.sprite.Group()
        self.all_bgs = pygame.sprite.LayeredUpdates()
        self.all_fgs = pygame.sprite.LayeredUpdates()
        self.invisible_blocks = pygame.sprite.Group()
        self.weather = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.eprojectiles = pygame.sprite.Group()#arrows and sword
        self.fprojectiles = pygame.sprite.Group()#arrows and sword
        self.loot = pygame.sprite.Group()
        self.enemy_pause = Entities.ExtendedGroup()#pygame.sprite.Group() #include all Entities that are far away
        self.npc_pause = pygame.sprite.Group() #include all Entities that are far away
        self.cosmetics = pygame.sprite.Group() #spirits
        self.camera_blocks = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.individuals = pygame.sprite.Group()
        self.all_Entities = pygame.sprite.Group()
        self.weather_paricles=BG.Weather(self.weather)#initiate whater
        #self.weather_paricles.create_particles('Snow')#weather effects
        self.reflection=BG.Reflection()
        #initiate player
        self.player = Entities.Player([200,50],self.fprojectiles,self.cosmetics)
        self.players = pygame.sprite.Group(self.player)
        self.player_center = (int(self.game.WINDOW_SIZE[0]/2),int(2*self.game.WINDOW_SIZE[1]/3))

    def load_map(self, map_name, spawn = '1'):
        self.map = map_loader.Level(map_name, self, spawn)
        self.initiate_groups()
        #self.load_bg_music()
        self.FADEIN = True
        self.BLACKEDOUT = True
        self.fade_count = 0

    def load_bg_music(self):
        try:
            self.sound.load_bg_sound(self.map.level_name)
            self.sound.play_bg_sound()
        except FileNotFoundError:
            print("No BG music found")

    def initiate_groups(self):
        #clean all groups
        #self.players.empty()
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.platforms_ramps.empty()
        self.enemy_pause.empty()
        self.npc_pause.empty()
        self.all_bgs.empty()
        self.all_fgs.empty()
        self.camera_blocks.empty()
        self.triggers.empty()

        #load all objects and art
        self.map.load_statics()
        self.map.load_collision_layer()
        self.map.load_bg()

    def collide_all(self):
        self.collisions.collide(self.players,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.enemies,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.npcs,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.loot,self.platforms, self.platforms_ramps)
        self.collisions.check_invisible(self.npcs,self.invisible_blocks)
        self.collisions.pickup_loot(self.player,self.loot)
        self.collisions.check_enemy_collision(self.player,self.enemies)

        #enter new state if new map is provided
        trigger = self.collisions.check_trigger(self.player,self.triggers)
        if trigger:
            if type(trigger).__name__ == 'Path_col':
                self.sound.pause_bg_sound()
                self.player.enter_idle()
                self.player.reset_movement()
                new_game_state = states.Fadeout(self.game, trigger.destination, trigger.spawn)
                new_game_state.enter_state()
                #self.load_map(trigger.destination, trigger.spawn)


        #if we make all abilities spirit based maybe we don't have to collide with all the platforms? and only check for enemy collisions?
        self.collisions.action_collision(self.fprojectiles,self.platforms,self.enemies)
        self.collisions.action_collision(self.eprojectiles,self.platforms,self.players)
        self.collisions.counter(self.fprojectiles,self.eprojectiles)

        self.collisions.weather_paricles(self.weather,self.platforms)#weather collisino. it is heavy

    def scrolling(self):
        self.map.scrolling(self.player.rect)
        scroll = [-self.map.camera.scroll[0],-self.map.camera.scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        self.platforms_ramps.update(scroll)
        self.all_bgs.update(scroll)
        self.all_fgs.update(scroll)
        self.players.update(scroll)
        self.enemies.update(scroll,self.player.rect.center)#shoudl the AI be based on playerposition?
        self.npcs.update(scroll)
        self.interactables.update(scroll)
        self.invisible_blocks.update(scroll)
        self.weather.update(scroll)
        self.fprojectiles.update(scroll)
        self.eprojectiles.update(scroll)
        self.loot.update(scroll)
        self.npc_pause.update(scroll)
        self.enemy_pause.update(scroll,self.player.rect.center)#shoudl the AI be based on playerposition?
        self.cosmetics.update(scroll)
        self.camera_blocks.update(scroll)
        self.triggers.update(scroll)

    def draw(self):

        self.all_bgs.draw(self.game.screen)
        self.weather.draw(self.game.screen)

        #self.platforms.draw(self.game.screen)
        self.interactables.draw(self.game.screen)
        self.enemies.draw(self.game.screen)
        self.npcs.draw(self.game.screen)
        self.players.draw(self.game.screen)
        self.fprojectiles.draw(self.game.screen)
        self.eprojectiles.draw(self.game.screen)
        self.loot.draw(self.game.screen)
        self.cosmetics.draw(self.game.screen)
        self.all_fgs.draw(self.game.screen)
        self.triggers.draw(self.game.screen)
        #self.camera_blocks.draw(self.game.screen)
        #self.reflection.draw(self.game.screen)
        #temporaries draws. Shuold be removed

        if self.game.RENDER_HITBOX_FLAG:
            for projectile in self.fprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), projectile.hitbox,2)#draw hitbox
            for projectile in self.eprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), projectile.hitbox,2)#draw hitbox
            #for enemy in self.enemies.sprites():#go through the group
            #    enemy.draw(self.game.screen)#add a glow around each enemy, can it be in group draw?
            for enemy in self.enemies.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), enemy.hitbox,2)#draw hitbox
                pygame.draw.rect(self.game.screen, (255,0,255), enemy.rect,2)#draw hitbox
            #for loot in self.loot.sprites():#go through the group
            #    pygame.draw.rect(self.game.screen, (0,0,255), loot.hitbox,2)#draw hitbox
            #    pygame.draw.rect(self.game.screen, (255,0,255), loot.rect,2)#draw hitbox

            pygame.draw.rect(self.game.screen, (0,0,255), self.player.hitbox,2)#draw hitbox
            pygame.draw.rect(self.game.screen, (255,0,255), self.player.rect,2)#draw hitbox

            for platform in self.platforms:#go through the group
                pygame.draw.rect(self.game.screen, (255,0,0), platform.hitbox,2)#draw hitbox
            for ramp in self.platforms_ramps:
                pygame.draw.rect(self.game.screen, (255,100,100), ramp.hitbox,2)#draw hitbox


    def conversation_collision(self):
        return Engine.Collisions.check_npc_collision(self.player,self.npcs)

    def interactions(self):
        change_map, chest_id = self.collisions.check_interaction(self.player,self.interactables)
        if change_map:
            self.change_map(change_map)
        elif chest_id:
            self.map_state[self.map.level_name]["chests"][chest_id][1] = "opened"

    def group_distance(self):#remove the entities if it is off screen from thir group
        bounds=[-100,600,-100,350]#-x,+x,-y,+y

        for entity in self.enemies:
            if entity.rect[0]<bounds[0] or entity.rect[0]>bounds[1] or entity.rect[1]<bounds[2] or entity.rect[1]>bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
                self.enemies.remove(entity)
                self.enemy_pause.add(entity)

        for entity in self.enemy_pause:
            if bounds[0]<entity.rect[0]<bounds[1] and bounds[2]<entity.rect[1]<bounds[3]: #or abs(entity.rect[1])<300:#this means it is outside of screen
                self.enemies.add(entity)
                self.enemy_pause.remove(entity)

        for entity in self.npcs:
            if entity.rect[0]<bounds[0] or entity.rect[0]>bounds[1] or entity.rect[1]<bounds[2] or entity.rect[1]>bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
                self.npcs.remove(entity)
                self.npc_pause.add(entity)

        for entity in self.npc_pause:
            if bounds[0]<entity.rect[0]<bounds[1] and bounds[2]<entity.rect[1]<bounds[3]: #or abs(entity.rect[1])<300:#this means it is outside of screen
                self.npcs.add(entity)
                self.npc_pause.remove(entity)


    #TODO: fix distance chek for remaining camera stops (right, left, top)
    def check_camera_border(self):

        xflag, yflag = False, False
        for stop in self.camera_blocks:
            if stop.dir == 'right':
                if (self.player.hitbox.centery - stop.rect.bottom < self.player_center[1]) and (stop.rect.top - self.player.hitbox.centery < self.game.WINDOW_SIZE[1] - self.player_center[1]):
                    #if -self.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.player.hitbox.centerx) < self.player_center[0]:
                    if -self.game.WINDOW_SIZE[0] < (stop.rect.centerx - self.player_center[0]) < self.player_center[0] and self.player.hitbox.centerx >= self.player_center[0]:
                        xflag = True
            elif stop.dir == 'left':
                if stop.rect.right >= 0 and self.player.hitbox.centerx < self.player_center[0]:
                    xflag = True
            elif stop.dir == 'bottom':
                if (stop.rect.left - self.player.hitbox.centerx < self.player_center[0]) and (self.player.hitbox.centerx - stop.rect.right < self.player_center[0]):
                    if (-self.game.WINDOW_SIZE[1] < (stop.rect.centery - self.player.hitbox.centery) < (self.game.WINDOW_SIZE[1] - self.player_center[1])):
                        yflag = True
            elif stop.dir == 'top':
                if (0 < stop.rect.left - self.player.hitbox.centerx < self.player_center[0]) or (0 < self.player.hitbox.centerx - stop.rect.right < self.player_center[0]):
                    if self.player.hitbox.centery - stop.rect.centery < 180 and stop.rect.bottom >= 0:
                        yflag = True

        if xflag and yflag:
            self.map.set_camera(3)
        elif xflag:
            self.map.set_camera(1)
        elif yflag:
            self.map.set_camera(2)
        else:
            self.map.set_camera(0)
