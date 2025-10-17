from .decision import Decision

class WaitDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def choose(self, player_distance, dt):
        state = self.entity.currentstate.state#the wait state
        
        state.wait_time -= dt        
        if state.wait_time <= 0:
            kwargs = {}
            kwargs['dir'] = state.dir#pass the dir in wait state
            return [Decision(
                next_state=state.next_state,
                score=50,
                priority=0,
                kwargs = kwargs
            )]
        
        return []