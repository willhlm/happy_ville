class StimulusTargetSelector:
    def __init__(self, entity, profile):
        self.entity = entity
        self.profile = profile
        self.current_source = None

    def get_target(self, fallback_target=None):
        manager = self.entity.game_objects.stimuli
        source = manager.find_best_source(
            self.entity,
            bounds=self.profile.get('bounds'),
            channel_weights=self.profile.get('channel_weights'),
            tag_weights=self.profile.get('tag_weights'),
            exclude_owners=self.profile.get('exclude_owners', []),
        )
        self.current_source = source

        if source is not None:
            return source.owner
        return fallback_target
