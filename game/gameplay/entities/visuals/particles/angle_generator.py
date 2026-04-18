import random
import math


class AngleGenerator:
    """Utility class for generating particle emission angles based on different distribution patterns."""
    
    @staticmethod
    def generate(dir, angle_spread=[30, 30], angle_dist=None):
        """
        Generate an angle based on direction and distribution type.
        
        Args:
            dir: Direction vector, float/int for specific angle, or 'isotropic' for random
            angle_spread: [lower_bound, upper_bound] for angle variance
            angle_dist: 'normal' for normal distribution, None for uniform
        
        Returns:
            angle in degrees
        """
        if dir == 'isotropic':
            return AngleGenerator._isotropic()
        elif isinstance(dir, (int, float)):
            return AngleGenerator._fixed_angle(dir)
        elif angle_dist == 'normal':
            return AngleGenerator._normal_distribution(dir, angle_spread)
        else:
            return AngleGenerator._directional(dir, angle_spread)
    
    @staticmethod
    def _isotropic():
        """Random angle in full 360 degrees."""
        return random.randint(-180, 180)
    
    @staticmethod
    def _fixed_angle(base_angle):
        """Angle with 180 degree flip and 30 degree spread."""
        base_angle += 180 * random.randint(0, 1)
        spawn_angle = 30
        return random.randint(base_angle - spawn_angle, base_angle + spawn_angle)
    
    @staticmethod
    def _directional(dir, angle_spread):
        """Angle based on direction vector with uniform distribution."""
        if dir[1] == -1:  # Hit from below
            spawn_angle = 30
            return random.randint(90 - spawn_angle, 90 + spawn_angle)
        elif dir[1] == 1:  # Hit from above
            spawn_angle = 30
            return random.randint(270 - spawn_angle, 270 + spawn_angle)
        elif dir[0] == -1:  # Right hit
            return random.randrange(0 - angle_spread[0], 0 + angle_spread[1])
        elif dir[0] == 1:  # Left hit
            return random.randrange(180 - angle_spread[1], 180 + angle_spread[0])
        else:
            # Fallback for other directions
            if dir[0] == 0:
                return 90
            else:
                return math.degrees(math.atan(dir[1] / dir[0]))
    
    @staticmethod
    def _normal_distribution(dir, angle_spread):
        """Angle based on direction vector with normal distribution."""
        if dir[1] == -1:  # Hit from below
            spawn_angle = 30
            return random.randint(90 - spawn_angle, 90 + spawn_angle)
        elif dir[1] == 1:  # Hit from above
            spawn_angle = 30
            return random.randint(270 - spawn_angle, 270 + spawn_angle)
        elif dir[0] == -1:  # Right hit
            mean = 0 + (angle_spread[1] - angle_spread[0]) / 2
            sigma = (angle_spread[1] + angle_spread[0]) / 2
            return random.normalvariate(mu=mean, sigma=sigma)
        elif dir[0] == 1:  # Left hit
            mean = 180 + (angle_spread[0] - angle_spread[1]) / 2
            sigma = (angle_spread[0] + angle_spread[1]) / 2
            return random.normalvariate(mu=mean, sigma=sigma)
        else:
            # Fallback
            if dir[0] == 0:
                return 90
            else:
                return math.degrees(math.atan(dir[1] / dir[0]))
