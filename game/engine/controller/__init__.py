"""Public input-controller API.

Import from ``engine.controller`` to access the public input-controller API.
"""

from .input import Controller
from .models import AxesSnapshot, InputAction, InputFrame

PROMPT_TYPES = ("keyboard", "xbox", "playstation", "nintendo")

__all__ = (
    "PROMPT_TYPES",
    "AxesSnapshot",
    "Controller",
    "InputAction",
    "InputFrame",
)
