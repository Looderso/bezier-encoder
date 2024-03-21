import numpy as np

from bezier_encoder.classes.points import Point, Points


def slerp(p1: Point | Points, p2: Point | Points, t: float | np.ndarray | list[float]) -> Point:
    """Perform spherical linear interpolation between two points on a sphere."""
    # Compute the cosine of the angle between the vectors
    if not np.isscalar(t):
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
    dot = p1.dot(p2)
    # Avoid a division by zero
    if dot > 0.9995:
        p = p1 + (p2 - p1) * t
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
