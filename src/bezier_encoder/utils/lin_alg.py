import math


def polar_to_cartesian(theta, phi, r):
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


def cartesian_to_polar(x, y, z):
    phi = math.acos(z)
    theta = math.atan2(y, x)
    r = math.sqrt(x**2 + y**2 + z**2)
    return theta, phi, r
