def apply_activation(sprite):
    if not hasattr(sprite, 'pause_group'):
        return
    if sprite.game_objects.activation_manager.is_active(sprite):
        return
    sprite.game_objects.activation_manager.sleep(sprite)


def unload_sprite(sprite):
    """Run map-lifecycle cleanup before releasing render resources."""
    on_map_unload = getattr(sprite, "on_map_unload", None)
    if callable(on_map_unload):
        on_map_unload()
    sprite.release_texture()

