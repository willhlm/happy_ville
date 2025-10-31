from gameplay.entities.enemies.base.enemy import Enemy

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.update_event(str(type(self).__name__).lower())

        self.game_objects.game.state_manager.enter_state(state_name = 'blit_image_text', image = self.game_objects.player.sprites[self.ability][0], text = self.ability)
        self.game_objects.game.state_manager.enter_state(state_name = 'defeated_boss')

    def give_abillity(self):
        self.game_objects.player.abilities.spirit_abilities[self.ability] = getattr(entities, self.ability)(self.game_objects.player)