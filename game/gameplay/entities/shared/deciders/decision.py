class Decision:
    def __init__(self, next_state, score=0, priority = 0, kwargs=None):
        self.next_state = next_state
        self.score = score
        self.priority = priority  # higher = overrides lower-priority deciders
        self.kwargs = kwargs or {}