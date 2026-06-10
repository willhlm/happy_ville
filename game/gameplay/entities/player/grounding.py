from engine import constants as C


class PlayerGrounding:
    def __init__(self, player):
        self.player = player

    def consume_contact_state(self):
        if self.player.is_on_floor():
            self.player.flags['ground'] = True
            self.end_coyote_time()
            return

        if self.player.was_on_floor():
            self.begin_coyote_time()
            return

    def on_coyote_timeout(self):
        self.player.flags['ground'] = False

    def begin_coyote_time(self):
        timer_manager = self.player.game_objects.timer_manager
        timer_manager.remove_ID_timer('cayote')
        timer_manager.start_timer(C.cayote_timer_player, self.on_coyote_timeout, ID='cayote')

    def end_coyote_time(self):
        self.player.game_objects.timer_manager.remove_ID_timer('cayote')
