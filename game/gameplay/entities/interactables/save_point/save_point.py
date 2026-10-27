import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_savepoint

class SavePoint(Interactables):
    SEJTE_ITEM_ID = 'sejte_stone'
    WORLD_STATE_BUCKET = 'save_point'
    # Five seconds in the game's frame-normalized time, leaving a comfortable interaction window after the save animation releases the player.
    INSTALL_WINDOW_DURATION = 300

    def __init__(self, pos, game_objects, map, save_point_id=None):
        super().__init__(pos, game_objects)
        self.sprites=read_files.load_sprites_dict('assets/sprites/entities/interactables/savepoint/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.save_point_id = str(save_point_id or map)
        self.init_cord = [pos[0],pos[1]-100]
        self.installed = self.game_objects.world_state.objects.load_bool(self.map, self.WORLD_STATE_BUCKET, self.save_point_id, initial=False)
        self.install_window_timer = None
        self.install_window_timer_id = f'save_point_install:{self.map}'
        self.currentstate = states_savepoint.Idle(self)    
        self.hit_component.set_invincibility(True)

        if self.installed:
            self._unlock_fast_travel()

    def interact(self, player=None):#when player press t/y
        player = player or self.game_objects.player
        if (self.install_window_timer is not None and not self.installed and player.backpack.inventory.get_quantity(self.SEJTE_ITEM_ID) > 0):
            self._open_install_confirmation(player)
            return

        self.activate(player)

    def activate(self, player):
        if not self.installed:
            self._start_install_window()
        player.currentstate.enter_state('crouch')
        player.backpack.map.save_savepoint(map =  self.map, point = self.init_cord)
        self.currentstate.handle_input('active')
        self.game_objects.ui.overlay.play_logo_loading(self.game_objects)

    def _open_install_confirmation(self, player):
        self.game_objects.game.state_manager.enter_state('confirmation', text='Place the Sejte Stone here?', on_confirm=lambda: self.install_sejte(player))

    def install_sejte(self, player):
        inventory = player.backpack.inventory
        if self.installed or inventory.get_quantity(self.SEJTE_ITEM_ID) <= 0:
            return False

        inventory.remove(self.SEJTE_ITEM_ID)
        self.installed = True
        self.game_objects.world_state.objects.set_bool(self.map, self.WORLD_STATE_BUCKET, self.save_point_id, True)
        self._unlock_fast_travel()
        self._close_install_window()
        self.activate(player)
        return True

    def _start_install_window(self):
        self._close_install_window()
        self.install_window_timer = self.game_objects.timer_manager.start_timer(self.INSTALL_WINDOW_DURATION, self._on_install_window_timeout, ID=self.install_window_timer_id)

    def _on_install_window_timeout(self):
        self.install_window_timer = None

    def _close_install_window(self):
        if self.install_window_timer is not None:
            self.install_window_timer.remove()
            self.install_window_timer = None

    def on_kill_cleanup(self):
        self._close_install_window()
        super().on_kill_cleanup()

    def _unlock_fast_travel(self):
        return self.game_objects.map_marker_manager.unlock(
            self.save_point_id,
            self.hitbox.center,
            room_id=self.map,
            spawn_position=list(self.init_cord),
            fast_travel=True,
        )
