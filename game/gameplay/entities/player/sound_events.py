from gameplay.entities.shared.components.audio_component import SoundEvent

"""Authored sound-event tuning for the player."""
PLAYER_SOUND_EVENTS = {
    "jump": SoundEvent("jump", relative_volume=0.5),
    "wall_jump": SoundEvent("jump", relative_volume=0.5),
    "dash": SoundEvent("dash", relative_volume=1.0),
    "footstep": SoundEvent("run", relative_volume=0.8),
    "pray": SoundEvent("pray", relative_volume=1.0),
}
