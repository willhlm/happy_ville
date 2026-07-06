# =========================
# overlay_manager.py
# =========================
from __future__ import annotations
from collections import defaultdict, deque
from typing import Deque, Dict, List, Optional

from engine.utils import read_files
from gameplay.data.narration_configs import get_narration_config
from gameplay.data.ui_overlay_configs import get_ui_overlay_config
from gameplay.ui.components.overlay.base_overlay import BaseOverlay
from gameplay.ui.components.overlay.animated_image_overlay import LogoLoadingOverlay
from gameplay.ui.components.overlay.text_overlay import TextOverlay


class OverlayLibrary:
    def __init__(self):
        self.narration_blocks = {}
        self.title_cards = {}
        self.textures = {}
        self.dynamic_cards = {}

    def add_title_cards(self, d):
        self.title_cards.update(d)

    def get_title(self, key):
        return self.title_cards[key]

    def add_textures(self, d):
        self.textures.update(d)

    def get_texture(self, key):
        return self.textures[key]

    def preload_narration(self, key):
        if key not in self.narration_blocks:
            self.narration_blocks[key] = get_narration_config(key)

    def get_narration(self, key):
        return self.narration_blocks[key]

    def preload_dynamic_overlay(self, game_objects, key):
        if key not in self.dynamic_cards:
            definition = get_ui_overlay_config(key)
            image = None
            image_path = definition.get("image_path")

            if image_path:
                image = game_objects.game.display.surface_to_texture(
                    read_files.load_sprite(image_path)
                )

            self.dynamic_cards[key] = {
                "loader_key": definition.get("loader_key", "default"),
                "image": image,
                "title": definition.get("title", ""),
                "text": definition.get("text", ""),
            }

    def get_dynamic_overlay(self, key):
        return self.dynamic_cards[key]

    def clear_map_assets(self):
        self.narration_blocks.clear()

        for card in self.dynamic_cards.values():
            image = card.get("image")
            if image:
                image.release()

        self.dynamic_cards.clear()

class OverlayManager:
    def __init__(self, game_objects):
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
    def preload_narration(self, key: str) -> None:
        self.overlay_library.preload_narration(key)

    def get_narration(self, key: str):
        return self.overlay_library.get_narration(key)

    def play_text_block(
        self,
        game_objects,
        *,
        lines,
        mode: str = "block",
        sound: str | None = None,
        channel: Optional[str] = "narration",
    ) -> None:
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
                sound=sound,
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
                    sound=sound,
                ))
                
    def play_static_overlay(self, game_objects, overlay_key: str, *, state_name: str = "static_overlay", callback=None) -> None:
        game_objects.game.state_manager.enter_state(state_name,overlay_key=overlay_key, callback=callback)

    def play_title_card(self, key):
        pass

    def preload_dynamic_overlay(self, game_objects, overlay_key: str) -> None:
        self.overlay_library.preload_dynamic_overlay(game_objects, overlay_key)

    def clear_map_assets(self) -> None:
        self.overlay_library.clear_map_assets()

    def play_logo_loading(self, game_objects, **kwargs) -> None:
        self.add(LogoLoadingOverlay(game_objects, **kwargs))

    def play_static_overlay(self, game_objects, overlay_key: str, *, state_name: str = "static_overlay", callback=None) -> None:
        game_objects.game.state_manager.enter_state(state_name,overlay_key=overlay_key, callback=callback)

    def play_dynamic_overlay(self, game_objects, overlay_key: str, *, callback=None) -> None:
        card = self.overlay_library.get_dynamic_overlay(overlay_key)
        game_objects.game.state_manager.enter_state(
            "dynamic_overlay",
            loader_key=card["loader_key"],
            image=card["image"],
            title=card["title"],
            text=card["text"],
            callback=callback,
        )
