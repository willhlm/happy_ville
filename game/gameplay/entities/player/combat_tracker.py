class CombatTracker:
    def __init__(self):
        self.swing = 0

    def next_swing_index(self):
        current = int(self.swing) + 1
        self.swing = not self.swing
        return current
