from gameplay.ui.components import HealthFrame, Health, SpiritFrame, Spirit, MovementHud, MoneyFrame

class HudMeters:
    HEALTH_APPEAR_SPEED = 0.0
    HEALTH_FADE_SPEED = 3.5
    HEALTH_VISIBLE_HOLD = 2.5
    HEALTH_IDLE_ALPHA = 0.0

    MONEY_APPEAR_SPEED = 0.0
    MONEY_FADE_SPEED = 4.0
    MONEY_VISIBLE_HOLD = 2.0
    MONEY_IDLE_ALPHA = 0.0

    def __init__(self, game_objects, *, offset=5):
        self.game_objects = game_objects
        self.offset = offset

        self.hearts = []
        self.spirits = []
        self.ability_hud = []

        self.money_frame = None
        self.money = 0
        self.money_pos = (self.offset, 50)
        self.number_pos = (self.offset + 24, 55)
        self.health_alpha = 1.0
        self.money_alpha = 0.0
        self.health_visible_timer = self.HEALTH_VISIBLE_HOLD
        self.money_visible_timer = 0.0

        self.init_hearts()
        self.init_spirits()
        self.init_ability()
        self.init_money()

    def _approach(self, current, target, speed, dt):
        if speed <= 0:
            return target
        step = min(1.0, speed * dt * 0.01)
        return current + (target - current) * step

    def _show_health(self):
        self.health_visible_timer = self.HEALTH_VISIBLE_HOLD

    def _show_money(self):
        self.money_visible_timer = self.MONEY_VISIBLE_HOLD

    def init_hearts(self):
        self.hearts = [HealthFrame(self.game_objects)]
        for i in range(0,self.game_objects.player.max_health - 1):
            self.hearts.append(Health(self.game_objects))
        self.update_hearts()

    def init_spirits(self):
        self.spirits = [SpiritFrame(self.game_objects)]
        for i in range(0,self.game_objects.player.max_spirit - 1):
            self.spirits.append(Spirit(self.game_objects))
        self.update_spirits()

    def init_ability(self):
        self.ability_hud = [MovementHud(self.game_objects.player)]

    def init_money(self):
        self.money_frame = MoneyFrame(self.game_objects.player)

    def update(self, dt):
        self.health_visible_timer = max(0.0, self.health_visible_timer - dt * 0.01)
        self.money_visible_timer = max(0.0, self.money_visible_timer - dt * 0.01)

        health_target = 1.0
        if self.game_objects.player.health >= self.game_objects.player.max_health and self.health_visible_timer <= 0:
            health_target = self.HEALTH_IDLE_ALPHA

        money_target = 1.0 if self.money_visible_timer > 0 else self.MONEY_IDLE_ALPHA

        health_speed = self.HEALTH_APPEAR_SPEED if health_target > self.health_alpha else self.HEALTH_FADE_SPEED
        money_speed = self.MONEY_APPEAR_SPEED if money_target > self.money_alpha else self.MONEY_FADE_SPEED

        self.health_alpha = self._approach(self.health_alpha, health_target, health_speed, dt)
        self.money_alpha = self._approach(self.money_alpha, money_target, money_speed, dt)

        for heart in self.hearts:
            heart.update(dt)
        for spirit in self.spirits:
            spirit.update(dt)
        for ability_hud in self.ability_hud:
            ability_hud.update(dt)

    def draw(self, target):
        h_pos = (14, 12)
        s_pos = (12, 12)
        frame_width = self.ability_hud[0].rect.width
        health_alpha = self.health_alpha
        money_alpha = self.money_alpha
        if health_alpha <= 0.01 and money_alpha <= 0.01:
            return

        for ability_hud in self.ability_hud:
            if health_alpha > 0.01:
                self.game_objects.shaders['alpha']['alpha'] = health_alpha * 255
                self.game_objects.game.display.render(ability_hud.image, target, position=(self.offset, self.offset), shader = self.game_objects.shaders['alpha'])

        for index, heart in enumerate(self.hearts):
            if health_alpha <= 0.01:
                break
            if index == 0:
                pos = (h_pos[0]*index + frame_width-3+self.offset, 7+self.offset)
            else:
                pos = (h_pos[0]*index + frame_width-5+self.offset, h_pos[1]+self.offset)
                self.game_objects.shaders['alpha']['alpha'] = health_alpha * 255
            self.game_objects.game.display.render(heart.image, target, position=pos, shader = self.game_objects.shaders['alpha'])

        for index, spirit in enumerate(self.spirits):
            continue
            if index == 0:
                pos = (5+self.offset, s_pos[1] * index + frame_width - 3+self.offset)
            else:
                pos = (s_pos[0]+self.offset, s_pos[1] * index + frame_width - 5+self.offset)
            self.game_objects.game.display.render(spirit.image, target, position=pos)

        if money_alpha > 0.01:
            alpha_255 = int(255 * money_alpha)
            self.game_objects.shaders['alpha']['alpha'] = alpha_255
            self.game_objects.game.display.render(self.money_frame.image, target, position=self.money_pos, shader = self.game_objects.shaders['alpha'])
            self.game_objects.game.display.render_text(
                self.game_objects.font.font_atals,
                target,
                str(self.money),
                position=self.number_pos,
                color=(255, 255, 255, alpha_255),
                letter_frame=None,
            )

    def update_money(self, num):
        self.money = num
        self._show_money()

    def remove_hearts(self,dmg):
        self._show_health()
        index = int(self.game_objects.player.health)-1
        index = max(index,-1)
        for i in range(index+int(dmg+0.5+self.game_objects.player.health-int(self.game_objects.player.health)),index,-1):
            health = self.hearts[i].health
            self.hearts[i].take_dmg(dmg)
            dmg -= health

    def update_hearts(self):
        self._show_health()
        for i in range(0,int(self.game_objects.player.health)):
            self.hearts[i].currentstate.handle_input('Idle')
        if self.game_objects.player.health - i - 1 == 0.5:
            self.hearts[i+1].currentstate.enter_state('Idle')
            self.hearts[i+1].take_dmg(0.5)

    def remove_spirits(self,spirit):
        self._show_health()
        index = self.game_objects.player.spirit + spirit - 1
        index = max(index,0)
        for i in range(index,index+spirit):
            self.spirits[i].currentstate.handle_input('Hurt')

    def update_spirits(self):
        self._show_health()
        for i in range(0,self.game_objects.player.spirit):
            self.spirits[i].currentstate.handle_input('Idle')
