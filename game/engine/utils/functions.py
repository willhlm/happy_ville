import math

def blur_radius(parallax, target_parallax = 1, min_blur=0.01, max_blur=10):
    mean_parallax = 0.5 * (parallax[0] + parallax[1])
    distance = abs(mean_parallax - target_parallax)  # distance from target
    # map distance to blur
    blur = min_blur + distance * (max_blur - min_blur)
    return min(blur, max_blur)

def sign(x):
    return (x > 0) - (x < 0)

def track_distance(position1, position2, r0 = 450, r1 = 120):
    # world positions
    px, py = position1
    sx, sy = position2

    d = math.hypot(px - sx, py - sy)

    # smoothstep amplitude
    if d >= r0:
       return 0.0
    elif d <= r1:
        return 1.0
    else:#smoothstep
        t = (r0 - d) / (r0 - r1)  # 0..1
        return t*t*(3 - 2*t)


