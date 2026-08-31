from .boss_reward_ball import BossRewardBall


def spawn_pending_boss_reward(game_objects, boss_id, boss_class, fallback_position):
    """Restore a defeated boss's uncollected reward during map loading."""
    narrative = game_objects.world_state.narrative
    if not narrative.is_boss_defeated(boss_id) or narrative.is_boss_reward_collected(boss_id):
        return None

    boss_cls = game_objects.registry.fetch('enemies', boss_class)
    if boss_cls is None:
        return None
    reward = boss_cls.build_reward_for_boss(game_objects, boss_id)
    if reward is None:
        return None

    position = narrative.get_boss_reward_position(boss_id) or fallback_position
    ball = BossRewardBall(position, game_objects, reward, boss_id)
    game_objects.interactables.add(ball)
    return ball
