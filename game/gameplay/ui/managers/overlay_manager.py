# =========================
# overlay_manager.py
# =========================
from __future__ import annotations
from collections import defaultdict, deque
from typing import Deque, Dict, List, Optional

from gameplay.ui.components.overlay.base_overlay import BaseOverlay
from gameplay.ui.components.overlay.text_overlay import TextOverlay


class OverlayLibrary:
    def __init__(self):
        self.text_blocks = {}
        self.title_cards = {}
        self.textures = {}

    def add_text_blocks(self, d):
        self.text_blocks.update(d)

    def add_title_cards(self, d):
        self.title_cards.update(d)

    def get_text(self, key):
        return self.text_blocks[key]

    def get_title(self, key):
        return self.title_cards[key]

class OverlayManager:
    def __init__(self):
        self.overlay_library = OverlayLibrary()

        # currently active overlays (all channels + channel-less)
        self.active: List[BaseOverlay] = []

        # per-channel: currently active overlay in that channel (if any)
        self._channel_current: Dict[str, BaseOverlay] = {}

        # per-channel: queued overlays waiting their turn
        self._channel_queue: Dict[str, Deque[BaseOverlay]] = defaultdict(deque)

    def _activate(self, item: BaseOverlay) -> None:
        """Make an overlay active and fire its start hook once."""
        self.active.append(item)
        item.on_start()

    def add(self, item: BaseOverlay) -> None:
        ch = getattr(item, "channel", None)

        # No channel => just add as normal (can overlap freely)
        if ch is None:
            self._activate(item)
            return

        # Channelled => queue semantics
        if ch not in self._channel_current:
            self._channel_current[ch] = item
            self._activate(item)
        else:
            self._channel_queue[ch].append(item)

    def update(self, dt: float) -> None:
        if not self.active:
            return

        # Update all active overlays
        for it in list(self.active):
            it.update(dt * 0.01)  # keep your existing scaling

        # Remove finished and promote queued
        finished = [it for it in self.active if getattr(it, "done", False)]
        if not finished:
            return

        for it in finished:
            self.active.remove(it)

            ch = getattr(it, "channel", None)
            if ch is not None and self._channel_current.get(ch) is it:
                if self._channel_queue[ch]:
                    nxt = self._channel_queue[ch].popleft()
                    self._channel_current[ch] = nxt
                    self._activate(nxt)
                else:
                    del self._channel_current[ch]

    def draw(self, target) -> None:
        for it in self.active:
            it.draw(target)

    # ----------------------------------------------------
    # Convenience: play narration from your text library
    # ----------------------------------------------------
    def play_text_block(
        self,
        game_objects,
        text_key: str,
        *,
        start_index: int = 0,
        count: int = 1,
        mode: str = "block",          # "block" or "sequential"
        channel: Optional[str] = "narration",
    ) -> None:

        lines_all = self.overlay_library.get_text(text_key)

        lines = lines_all[start_index:start_index + count]

        w, h = game_objects.game.window_size
        box_w = int(w * 0.6)
        box_left = (w - box_w) // 2
        box_top = int(h * 0.8)

        fade_in = 0.25
        hold = 1.6
        fade_out = 0.35
        delay = 0.0        

        if mode == "block":
            self.add(TextOverlay(
                game_objects,
                lines,
                box_left=box_left,
                box_top=box_top,
                box_width=box_w,
                fade_in=fade_in,
                hold=hold,
                fade_out=fade_out,
                delay=delay,
                channel=channel,
            ))
        else:
            for line in lines:
                self.add(TextOverlay(
                    game_objects,
                    [line],
                    box_left=box_left,
                    box_top=box_top,
                    box_width=box_w,
                    fade_in=fade_in,
                    hold=hold,
                    fade_out=fade_out,
                    delay=delay,
                    channel=channel,
                ))

    def play_title_card(self, key):
        pass