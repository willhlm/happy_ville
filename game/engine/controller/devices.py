"""SDL controller discovery and prompt-family detection."""

import pygame._sdl2.controller


def discover_controllers():
    return [
        pygame._sdl2.controller.Controller(controller_id)
        for controller_id in range(pygame._sdl2.controller.get_count())
    ]


def detect_prompt_type(name):
    name = name.lower()
    if any(term in name for term in ("playstation", "dualshock", "dualsense", "sony")):
        return "playstation"
    if any(term in name for term in ("nintendo", "switch", "joy-con", "joycon")):
        return "nintendo"
    return "xbox"


def controller_types(controllers):
    return {
        controller.id: detect_prompt_type(controller.name) for controller in controllers
    }
