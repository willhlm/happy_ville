def apply_activation(sprite):
    if not hasattr(sprite, 'pause_group'):
        return
    if sprite.game_objects.activation_manager.is_active(sprite):
        return
    sprite.game_objects.activation_manager.sleep(sprite)

