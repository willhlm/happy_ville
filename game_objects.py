import pygame, sys
import Read_files
import Engine
import Entities
import Level
import BG

class Game_Objects():

    def __init__(self, game):

        self.game = game
        self.map_state = Read_files.read_json("map_state.json") #check this file for structure of object
        pygame.mixer.init
        self.bg_music = pygame.mixer.Channel(0)
        self.collisions = Engine.Collisions()
        self.create_groups()

    def create_groups(self):

        #initiate player
        self.player = Entities.Player([200,50])
        self.players = pygame.sprite.Group(self.player)
        self.player_center = (self.game.WINDOW_SIZE[0]/2,2*self.game.WINDOW_SIZE[1]/3)

        #define all sprite groups
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bg_fixed = pygame.sprite.Group()
        self.bg_far = pygame.sprite.Group()
        self.bg_mid = pygame.sprite.Group()
        self.bg_near = pygame.sprite.Group()
        self.fg_fixed = pygame.sprite.Group()
        self.fg_paralex = pygame.sprite.Group()
        self.bgs = [self.bg_fixed,self.bg_far,self.bg_mid,self.bg_near,self.fg_fixed,self.fg_paralex]
        self.invisible_blocks = pygame.sprite.Group()
        self.weather = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.fprojectiles = pygame.sprite.Group()#arrows and sword
        self.eprojectiles = pygame.sprite.Group()#arrows and sword
        self.loot = pygame.sprite.Group()
        self.enemy_pause = pygame.sprite.Group() #include all Entities that are far away
        self.npc_pause = pygame.sprite.Group() #include all Entities that are far away
        self.cosmetics = pygame.sprite.Group() #spirits
        self.camera_blocks = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.platforms_pause=pygame.sprite.Group()
        self.individuals = pygame.sprite.Group()
        self.all_Entities = pygame.sprite.Group()
        self.weather_paricles=BG.Weather()#initiate whater
        self.weather = self.weather_paricles.create_particle('Snow')#weather effects

    def load_map(self, map_name):
        self.map = Level.Tilemap(map_name, self.player_center)
        self.initiate_groups()
        self.load_music()

    def change_map(self, map_name):
        #actually load the new map
        self.load_map(map_name)

    def load_music(self):
        self.bg_music.play(self.map.load_bg_music(),-1)
        self.bg_music.set_volume(0.1)

    def initiate_groups(self):

        #clean all groups
        #self.players.empty()
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.platforms_pause.empty()
        self.enemy_pause.empty()
        self.npc_pause.empty()

        #load all objects
        player_pos, self.npcs, self.enemies, self.interactables, self.triggers, self.camera_blocks = self.map.load_statics(self.map_state[self.map.level_name])
        self.player.set_pos(player_pos)
        self.platforms,self.platforms_pause=self.map.load_map()#load all map
        #self.players.add(self.player)

        #clean and load bg
        for bg in self.bgs:
            bg.empty()
        for i, bg in enumerate(self.map.load_bg()):
            self.bgs[i].add(bg)

    def collide_all(self):
        self.collisions.collide(self.players,self.platforms)
        self.collisions.collide(self.enemies,self.platforms)
        self.collisions.collide(self.npcs,self.platforms)
        self.collisions.collide(self.loot,self.platforms)
        self.collisions.check_invisible(self.npcs,self.invisible_blocks)
        self.collisions.pickup_loot(self.player,self.loot)
        self.collisions.check_enemy_collision(self.player,self.enemies)

    def scrolling(self):
        self.map.scrolling(self.player.rect,self.collisions.shake)
        scroll = [-self.map.camera.scroll[0],-self.map.camera.scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        self.platforms_pause.update(scroll)

        for bg in self.bgs:
            bg.update(scroll)
        self.players.update(scroll)
        self.enemies.update(scroll)
        self.npcs.update(scroll)
        self.interactables.update(scroll)
        self.invisible_blocks.update(scroll)
        self.weather.update(scroll,self.game.screen)
        self.fprojectiles.update(scroll)
        self.eprojectiles.update(scroll)
        self.loot.update(scroll)
        self.npc_pause.update(scroll)
        self.enemy_pause.update(scroll)
        self.cosmetics.update(scroll)
        self.camera_blocks.update(scroll)
        self.triggers.update(scroll)

    def draw(self):
        for i in range(1,4):
            self.bgs[i].draw(self.game.screen)
        self.bg_fixed.draw(self.game.screen)
        #self.weather.draw(self.game.screen)

        #self.platforms.draw(self.game.screen)
        self.interactables.draw(self.game.screen)
        self.enemies.draw(self.game.screen)
        self.npcs.draw(self.game.screen)
        self.players.draw(self.game.screen)
        self.fprojectiles.draw(self.game.screen)
        self.eprojectiles.draw(self.game.screen)
        self.loot.draw(self.game.screen)
        self.cosmetics.draw(self.game.screen)
        for i in range(4,6):
            self.bgs[i].draw(self.game.screen)
        self.triggers.draw(self.game.screen)
        #self.camera_blocks.draw(self.game.screen)

    def interactions(self):
        change_map, chest_id = self.collisions.check_interaction(self.player,self.interactables)
        if change_map:
            self.change_map(change_map)
        elif chest_id:
            self.map_state[self.map.level_name]["chests"][chest_id][1] = "opened"

    def trigger_event(self):
        change_map = self.collisions.check_trigger(self.player,self.triggers)
        if change_map:
            self.change_map(change_map)

    def group_distance(self):#remove the eneteies if it is off screen from thir group
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

        self.platforms,self.platforms_pause=self.map.update_chunks()#update the rellavant pltforms

    def check_camera_border(self):

        xflag, yflag = False, False
        for stop in self.camera_blocks:
            if stop.dir == 'right':
                if (stop.rect.centerx - self.player.rect.centerx) < self.game.WINDOW_SIZE[0]/2:
                    xflag = True
            elif stop.dir == 'left':
                if stop.rect.right >= 0 and self.player.rect.centerx < self.game.WINDOW_SIZE[0]/2:
                    xflag = True
            elif stop.dir == 'bottom':
                if (stop.rect.centery - self.player.rect.centery) < (self.game.WINDOW_SIZE[1] - 180):
                    yflag = True
            elif stop.dir == 'top':
                if self.player.rect.centery - stop.rect.centery < 180 and stop.rect.bottom >= 0:
                    yflag = True

        if xflag and yflag:
            self.map.set_camera(3)
        elif xflag:
            self.map.set_camera(1)
        elif yflag:
            self.map.set_camera(2)
        else:
            self.map.set_camera(0)