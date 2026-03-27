import math
import random


def get_tagg_burst_chain_cooldown(entity):
    cooldown = entity.config['cooldowns']['tagg_burst_chain']
    return random.randint(cooldown[0], cooldown[1])


def get_tagg_burst_repeat_cooldown(entity):
    cooldown = entity.config['cooldowns']['tagg_burst_repeat']
    return random.randint(cooldown[0], cooldown[1])


def get_tagg_burst_profile(entity):
    attack_cfg = entity.config['attacks']['tagg_burst']
    return (
        random.choice(attack_cfg['counts']),
        random.uniform(attack_cfg['speed'][0], attack_cfg['speed'][1]),
    )


def get_tagg_burst_volley_count(entity):
    volleys = entity.config['attacks']['tagg_burst']['volleys']
    return random.randint(volleys[0], volleys[1])


def get_player_aligned_burst_offset(entity, count):
    player_distance = entity.currentstate.player_distance
    angle = math.atan2(player_distance[1], player_distance[0])
    step = math.tau / count
    base_angle = round(angle / step) * step
    stagger_offset = (entity.tagg_burst_index % 2) * (step * 0.5)
    return base_angle + stagger_offset


def get_retreat_time(entity):
    retreat_time = entity.config['timers']['retreat_after_burst']
    return random.randint(retreat_time[0], retreat_time[1])
