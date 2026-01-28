def blur_radius(parallax, target_parallax = 1, min_blur=0.01, max_blur=10):
    mean_parallax = 0.5 * (parallax[0] + parallax[1])
    distance = abs(mean_parallax - target_parallax)  # distance from target
    # map distance to blur
    blur = min_blur + distance * (max_blur - min_blur)
    return min(blur, max_blur)

def sign(x):
    return (x > 0) - (x < 0)