import math

import numpy as np


def build_gaussian_kernel(radius, max_radius=31, array_size=64):
    r_int = int(max(0, min(max_radius, round(float(radius)))))
    weights = np.zeros(array_size, dtype="f4")

    if r_int == 0:
        weights[0] = 1.0
        return r_int, weights

    sigma = max(float(radius), 0.001)
    values = [math.exp(-0.5 * (i * i) / (sigma * sigma)) for i in range(r_int + 1)]
    total = values[0] + 2.0 * sum(values[1:])

    for i, value in enumerate(values):
        weights[i] = value / total

    return r_int, weights
