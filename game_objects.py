import pygame, sys
import Read_files
import Engine
import Entities
import Level
import BG

class Game_Objects():

    def __init__(self, game):

        self.create_groups()
        self.game = game

    def create_groups(self):

        #initiate player
        self.player = Entities.Player([200,50])
        self.players = pygame.sprite.Group(self.player)
        self.player_center = (216,180)

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
        self.enemy_pause = pygame.sprite.Group() #include all entities that are far away
        self.npc_pause = pygame.sprite.Group() #include all entities that are far away
        self.cosmetics = pygame.sprite.Group() #spirits
        self.camera_blocks = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.platforms_pause=pygame.sprite.Group()
        self.individuals = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()
        self.weather_paricles=BG.Weather()#initiate whater
        self.weather = self.weather_paricles.create_particle('Snow')#weather effects

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

    def change_map(self, map_name):
        timer = 0
        load_time = 50
        self.bg_music.fadeout(int(1000*load_time/60))
        #fade before loading new map
        while timer < load_time:
            self.game.screen.fill((207,238,250))
            self.interactables.update((0,0))
            self.draw()
            self.blit_screen_info()
            fade_surface = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
            fade_surface.fill((0,0,0,int(timer*255/load_time)))
            self.game.screen.blit(fade_surface,(0,0))
            self.display.blit(pygame.transform.scale(self.game.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen
            pygame.display.update()#update after every change
            self.clock.tick(60)#limmit FPS
            timer += 1

        #actually load the new map
        self.load_map(map_name)
        self.game_loop(True)

    def load_map(self, map_name):
        self.map = Level.Tilemap(map_name, self.player_center)
        self.initiate_groups()
        self.load_music()

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
