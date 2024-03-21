import numpy as np

from bezier_encoder.classes.points import PointCartesian


def slerp(p1: PointCartesian, p2: PointCartesian, t) -> PointCartesian:
    """Perform spherical linear interpolation between two points on a sphere."""
    # Compute the cosine of the angle between the vectors
    dot = p1.dot(p2)
    # Avoid a division by zero
    if dot > 0.9995:
        p = p1 + t * (p2 - p1)
        return p

    # Compute the actual angle
    theta = np.arccos(dot)
    sin_theta = np.sin(theta)

    # Compute the spherical linear interpolation
    s1 = np.sin((1 - t) * theta) / sin_theta
    s2 = np.sin(t * theta) / sin_theta
    p = p1 * s1 + p2 * s2

    # Convert back to polar coordinates
    return p
