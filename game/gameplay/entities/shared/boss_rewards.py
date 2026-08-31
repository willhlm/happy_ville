from dataclasses import dataclass


@dataclass(frozen=True)
class BossReward:
    def apply(self, player):
        raise NotImplementedError

    def get_instruction_key(self):
        raise NotImplementedError


@dataclass(frozen=True)
class ProgressionUnlockReward(BossReward):
    progress_key: str

    def apply(self, player):
        player.progression.unlock(self.progress_key)

    def get_instruction_key(self):
        return self.progress_key
