from typing import Protocol

class BaseOverlay(Protocol):
    """Interface for anything that can be drawn as an overlay."""
    done = False
    channel = None

    def on_start(self) -> None:
        pass

    def update(self, dt: float):
        pass

    def draw(self, target):
        pass