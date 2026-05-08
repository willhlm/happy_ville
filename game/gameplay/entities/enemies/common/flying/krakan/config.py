ENEMY_CONFIG = {
    'krakan': {
        'health': 3,
        'speeds': {
            'chase': 3.8,
            'dive': 8,
            'fall': 0.5,
            'fall_max': 1.2,
            'ground_snap': 0.35,
        },
        'patrol': {
            'home_radius': [150, 120],
            'ground_speed': 0.12,
            'ground_leash': 20,
            'grounded_grace_time': 8,
            'takeoff_boost': 5,
            'takeoff_forward_boost': 1.8,
            'takeoff_rise_speed': 3.8,
            'takeoff_rise_response': 0.7,
            'takeoff_end_height': 20,
            'wander_time': [20, 45],
            'wander_chance': 0.45,
        },
        'hover': {
            'height': 100,
            'side_offset': 52,
            'vertical_deadzone': 50,
            'follow_speed': 2.0,
            'orbit_radius_x': 200,
            'orbit_radius_y': 50,
            'cross_speed': 0.06,
        },
        'distances': {
            'aggro': [230, 150],
            'attack': [110, 170],
        },
        'attack': {
            'line_up_speed': 1,
            'turns_before_dive': [3, 4],
            'give_up_time': 220,
            'retreat_speed': 0.36,
            'retreat_time': 48,
            'retreat_height': 84,
            'retreat_distance': 108,
        },

        'timers': {'hurt_recovery': [150, 200]},
        'cooldowns': {'melee_attack': [150, 250]},#min max
        'states': {
            'patrol': {},
            'ground_walk': {},
            'air_patrol': {},
            'chase': {},
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
            'hurt': {},
        }
    }
}
