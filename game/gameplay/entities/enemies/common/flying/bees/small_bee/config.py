ENEMY_CONFIG = {
    'mygga': {
        'health': 1,
        'speeds': {
            'patrol': 0.14,
            'chase': 0.75,
            'swarm': 0.48,
            'attack': 4.2,
        },
        'distances': {
            'aggro': [220, 150],
            'attack': [120, 95],
        },
        'behavior': {
            'patrol_radius': [50, 28],
            'swarm_side_offset': [18, 42],
            'swarm_height_offset': [-26, 20],
            'swarm_weave_x': 14,
            'swarm_weave_y': 10,
            'swarm_weave_speed': 0.055,
            'attack_commit_time': [22, 40],
            'attack_pre_time': 10,
            'post_attack_delay': [24, 42],
            'charge_release_distance': 72,
            'give_up_time': 320,
        },

        'timers': {'hurt_recovery': [150, 200]},
        'cooldowns': {'melee_attack': [90, 150]},#min max
        'states': {
            'patrol': {},
            'chase': {},
            'attack_pre': {},
            'attack_main': {},
        }
    }
}
