from .backpack_pages import InventoryUI, JournalUI, MapUI, RadnaUI


class BackpackUiManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.screen = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.pages = {
            'inventory': InventoryUI(game_objects),
            'map': MapUI(game_objects),
            'radna': RadnaUI(game_objects),
            'journal': JournalUI(game_objects),
        }
        self.page_order = ['map', 'inventory', 'radna', 'journal']
        self.active_page_ui = None
        self.active_page = None
        self.index = 0

    def update(self, dt):
        if self.active_page_ui is None:
            return
        self.active_page_ui.update(dt)

    def render(self):
        if self.active_page_ui is None:
            return
        self.active_page_ui.render()

    def handle_events(self, input):
        if self.active_page_ui is None:
            return
        self.active_page_ui.handle_events(input)

    def set_page(self, page, **kwarg):
        previous_ui = self.active_page_ui
        if previous_ui is not None and previous_ui is not self.pages[page]:
            previous_ui.on_exit()

        next_ui = self.pages[page]
        next_ui.on_enter(**kwarg)
        self.active_page_ui = next_ui
        self.active_page = page
        self.index = self.get_available_pages().index(page)

    def open_page(self, page, **kwarg):
        available_pages = self.get_available_pages()
        if page not in available_pages:
            raise KeyError(f'UI page "{page}" is not available')
        self.set_page(page, **kwarg)

    def close_page(self):
        if self.active_page_ui is not None:
            self.active_page_ui.on_exit()
        self.active_page_ui = None
        self.active_page = None

    def next_page(self, **kwarg):
        available_pages = self.get_available_pages()
        if not available_pages:
            return
        self.index = min(self.index + 1, len(available_pages) - 1)
        self.set_page(available_pages[self.index], **kwarg)

    def previous_page(self, **kwarg):
        available_pages = self.get_available_pages()
        if not available_pages:
            return
        self.index = max(self.index - 1, 0)
        self.set_page(available_pages[self.index], **kwarg)

    def get_available_pages(self):
        holdings = self.game_objects.player.backpack.holdings.keys()
        return [
            page for page in self.page_order
            if page in holdings and page in self.pages
        ]
