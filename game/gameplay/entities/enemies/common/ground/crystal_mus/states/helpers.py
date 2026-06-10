import random

def get_tagg_burst_repeat_cooldown(entity):
    cooldown = entity.config['cooldowns']['tagg_burst_repeat']
    return random.randint(cooldown[0], cooldown[1])


def get_retreat_time(entity):
    retreat_time = entity.config['timers']['retreat_after_burst']
    return random.randint(retreat_time[0], retreat_time[1])
