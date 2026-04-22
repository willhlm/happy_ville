ENEMY_CONFIG = {
    'krakan': {
        'health': 3,
        'speeds': {
            'ground': 0.12,
            'landing': 0.5,
            'landing_max': 1.2,
            'ground_snap': 0.35,
            'takeoff': 0.26,
            'chase': 0.3,
            'line_up': 0.34,
            'retreat': 0.36,
            'dive': 3.8,
        },
        'distances': {
            'aggro': [220, 150],
            'attack': [110, 170],
        },
        'behavior': {
            'home_radius': [150, 120],
            'hover_height': 100,
            'hover_side_offset': 52,
            'hover_vertical_deadzone': 50,
            'hover_follow_speed': 1.2,
            'hover_span': 60,
            'hover_cross_speed': 0.035,
            'hover_bob_height': 10,
            'hover_bob_speed': 0.06,
            'attack_turns': [2, 3],
            'retreat_height': 84,
            'retreat_distance': 108,
            'ground_leash': 20,
            'grounded_grace_time': 8,
            'ground_wander_time': [20, 45],
            'ground_wander_chance': 0.45,
            'give_up_time': 220,
            'retreat_time': 48,
            'attack_pre_time': 18,
            'attack_commit_distance': [18, 24],
        },

        'timers': {'hurt_recovery': [150, 200]},
        'cooldowns': {'melee_attack': [150, 250]},#min max
        'states': {
            'patrol': {},
            'chase': {},
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
            'hurt': {},
        }
    }
}
