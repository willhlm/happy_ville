"""Public input-controller API.

Import from ``engine.controller`` to access the public input-controller API.
"""

from .bindings import (
    ALL_ACTIONS,
    BUTTON_ACTIONS,
    DIRECTION_ACTIONS,
    BindingStore,
)
from .input import Controller
from .models import AxesSnapshot, InputAction, InputFrame

PROMPT_TYPES = ("keyboard", "xbox", "playstation", "nintendo")

__all__ = (
    "ALL_ACTIONS",
    "BUTTON_ACTIONS",
    "DIRECTION_ACTIONS",
    "PROMPT_TYPES",
    "AxesSnapshot",
    "BindingStore",
    "Controller",
    "InputAction",
    "InputFrame",
)
