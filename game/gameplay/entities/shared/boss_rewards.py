from dataclasses import dataclass


@dataclass(frozen=True)
class BossReward:
    preview_sprite: str

    def apply(self, player):
        raise NotImplementedError


@dataclass(frozen=True)
class ProgressionUnlockReward(BossReward):
    progress_key: str

    def apply(self, player):
        player.progression.unlock(self.progress_key)
