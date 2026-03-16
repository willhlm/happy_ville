import pygame
from gameplay.ui.components import HealthFrame, Health, SpiritFrame, Spirit, MovementHud, MoneyFrame

class HUD():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.blur_screen = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.offset = 5

        self.init_hearts()
        self.init_spirits()
        self.init_ability()
        self.init_money()

    def init_hearts(self):
        self.hearts = []
        self.hearts.append(HealthFrame(self.game_objects))
        for i in range(0,self.game_objects.player.max_health - 1):#make hearts
            self.hearts.append(Health(self.game_objects))
        self.update_hearts()

    def init_spirits(self):
        self.spirits = []
        self.spirits.append(SpiritFrame(self.game_objects))
        for i in range(0,self.game_objects.player.max_spirit - 1):#make hearts
            self.spirits.append(Spirit(self.game_objects))
        self.update_spirits()

    def init_ability(self):
        self.ability_hud = []#the hud
        self.ability_hud.append(MovementHud(self.game_objects.player))#the ability object
        
    def init_money(self):
        self.money_frame = MoneyFrame(self.game_objects.player)
        self.money = 0

        self.money_pos = (self.offset, 50)
        self.number_pos = (self.offset + 24, 55)

    def update_money(self, num):
        self.money = num

    def update(self, dt):
        for heart in self.hearts:
            heart.update(dt)
        for spirit in self.spirits:
            spirit.update(dt)
        for ability_hud in self.ability_hud:
            ability_hud.update(dt)

        self.update_overlay(dt)

    def update_overlay(self, dt):
        self.game_objects.ui.overlay.update(dt)

    def draw(self, composite_screen):
        h_pos = (14, 12)
        s_pos = (12, 12)
        frame_width = self.ability_hud[0].rect.width
        self.blur_screen.clear(0,0,0,0)
        self.screen.clear(0,0,0,0)

        for index,ability_hud in enumerate(self.ability_hud):#draw movement ability_hud
            self.game_objects.game.display.render(ability_hud.image,self.blur_screen, position = (self.offset, self.offset))

        for index, heart in enumerate(self.hearts):#draw health
            if index == 0:
                pos = (h_pos[0]*index + frame_width-3+self.offset, 7+self.offset)
            else:
                pos = (h_pos[0]*index + frame_width-5+self.offset, h_pos[1]+self.offset)
            self.game_objects.game.display.render(heart.image,self.blur_screen, position = pos)

        for index, spirit in enumerate(self.spirits):#draw spirit
            continue
            if index == 0:
                pos = (5+self.offset, s_pos[1] * index + frame_width - 3+self.offset)
            else:
                pos = (s_pos[0]+self.offset, s_pos[1] * index + frame_width - 5+self.offset)
            self.game_objects.game.display.render(spirit.image,self.blur_screen, position = pos)

        self.game_objects.game.display.render(self.money_frame.image, self.blur_screen, position = self.money_pos)
        self.game_objects.game.display.render_text(self.game_objects.font.font_atals, self.blur_screen, str(self.money), position=self.number_pos, color=(255, 255, 255, 255), letter_frame=None)

        self.game_objects.shaders['blur_outline']['blurRadius'] = 1
        self.game_objects.game.display.render(self.blur_screen.texture, self.screen, shader = self.game_objects.shaders['blur_outline'])
        self.render_fps()#render on scren, witout blur             
        self.render_overlay(self.screen)        
        self.game_objects.game.display.render(self.screen.texture, composite_screen, scale = self.game_objects.game.scale)         

    def render_overlay(self, target):
        self.game_objects.game.display.use_premultiplied_alpha_mode()   
        self.game_objects.ui.overlay.draw(target)
        self.game_objects.game.display.use_standard_alpha_mode()

    def render_fps(self):
        if self.game_objects.game.RENDER_FPS_FLAG:
            fps_string = str(int(self.game_objects.game.game_loop.clock.get_fps()))
            text = 'fps ' + fps_string
            self.game_objects.game.display.render_text(self.game_objects.font.font_atals, self.screen, text, letter_frame = None, color = (255,255,255,255), position = (self.screen.width - 50, 10))

    def remove_hearts(self,dmg):#dmg is 0.5, 1 or 2. Will set the rellavant to hurt
        index = int(self.game_objects.player.health)-1
        index = max(index,-1)
        for i in range(index+int(dmg+0.5+self.game_objects.player.health-int(self.game_objects.player.health)),index,-1):
            health = self.hearts[i].health
            self.hearts[i].take_dmg(dmg)
            dmg -= health#distribute the dmg

    def update_hearts(self):#set the rellavant onces to idle
        for i in range(0,int(self.game_objects.player.health)):#set them to idle for the number of health we have
            self.hearts[i].currentstate.handle_input('Idle')
        if self.game_objects.player.health - i - 1 == 0.5:
            self.hearts[i+1].currentstate.enter_state('Idle')
            self.hearts[i+1].take_dmg(0.5)

    def remove_spirits(self,spirit):
        index = self.game_objects.player.spirit + spirit - 1
        index = max(index,0)#in principle not needed but make it fool proof
        for i in range(index,index+spirit):
            self.spirits[i].currentstate.handle_input('Hurt')#make heart go white

    def update_spirits(self):#set the rellavant onces to idle
        for i in range(0,self.game_objects.player.spirit):#set them to idle for the number of health we have
            self.spirits[i].currentstate.handle_input('Idle')
