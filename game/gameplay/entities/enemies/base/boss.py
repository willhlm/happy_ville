from gameplay.entities.enemies.base.enemy import Enemy

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10
        #self.health_bar = entities.Health_bar(self)

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.update_event(str(type(self).__name__).lower())

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites[self.ability][0], text = self.ability)
        self.game_objects.game.state_manager.enter_state(state_name = 'Defeated_boss', category = 'game_states_cutscenes')

    def health_bar(self):#called from omamori Boss_HP
        self.health_bar.max_health = self.health
        self.game_objects.cosmetics.add(self.health_bar)

    def give_abillity(self):
        self.game_objects.player.abilities.spirit_abilities[self.ability] = getattr(entities, self.ability)(self.game_objects.player)

    def knock_back(self,**kwarg):
        pass