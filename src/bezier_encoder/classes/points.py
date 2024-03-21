from __future__ import annotations

import numpy as np

import bezier_encoder.classes.coordinates as coordinates
import bezier_encoder.utils.lin_alg as lin_alg


class PointCartesian:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.data: np.ndarray = np.array([x, y, z])

    @classmethod
    def from_polar(cls, phi: float, theta: float, r: float):
        x, y, z = lin_alg.polar_to_cartesian(phi, theta, r)
        return cls(x, y, z)

    @classmethod
    def from_data(cls, data: np.ndarray):
        assert data.ndim == 1
        assert data.size == 3
        return cls(data[0], data[1], data[2])

    @property
    def x(self):
        return self.data[coordinates.X]

    @x.setter
    def x(self, x: float):
        self.data[coordinates.X] = x

    @property
    def y(self):
        return self.data[coordinates.Y]

    @y.setter
    def y(self, y: float):
        self.data[coordinates.Y] = y

    @property
    def z(self):
        return self.data[coordinates.Z]

    @z.setter
    def z(self, z: float):
        self.data[coordinates.Z] = z

    def dot(self, other: PointCartesian) -> float:
        return np.sum(self.data * other.data)  # type: ignore

    def __add__(self, other: PointCartesian | float | int):
        if isinstance(other, PointCartesian):
            return PointCartesian.from_data(self.data + other.data)
        return PointCartesian.from_data(self.data + other)

    def __sub__(self, other: PointCartesian | float | int):
        if isinstance(other, PointCartesian):
            return PointCartesian.from_data(self.data - other.data)
        return PointCartesian.from_data(self.data - other)

    def __mul__(self, other: PointCartesian | float | int):
        if isinstance(other, PointCartesian):
            return PointCartesian.from_data(self.data * other.data)
        return PointCartesian.from_data(self.data * other)

    def __truediv__(self, other: PointCartesian | float | int):
        if isinstance(other, PointCartesian):
            return PointCartesian.from_data(self.data / other.data)
        return PointCartesian.from_data(self.data / other)

    def to_polar(self) -> PointPolar:
        return PointPolar.from_cartesian(self.x, self.y, self.z)


class PointPolar:
    def __init__(self, phi: float, theta: float, r: float) -> None:
        self.data = np.array([phi, theta, r])

    @classmethod
    def from_cartesian(cls, x: float, y: float, z: float):
        phi, theta, r = lin_alg.cartesian_to_polar(x, y, z)
        return cls(phi, theta, r)

    @property
    def phi(self):
        return self.data[coordinates.PHI]

    @phi.setter
    def phi(self, phi: float):
        self.data[coordinates.PHI] = phi

    @property
    def theta(self):
        return self.data[coordinates.THETA]

    @theta.setter
    def theta(self, theta: float):
        self.data[coordinates.THETA] = theta

    @property
    def r(self):
        return self.data[coordinates.R]

    @r.setter
    def r(self, r: float):
        self.data[coordinates.R] = r

    def to_cartesian(self) -> PointCartesian:
        return PointCartesian.from_polar(self.phi, self.theta, self.r)


class Rotation:
    def __init__(self, yaw: float, pitch: float, roll: float) -> None:
        self.data = np.array([yaw, pitch, roll])

    @property
    def yaw(self):
        return self.data[coordinates.YAW]

    @yaw.setter
    def yaw(self, yaw: float):
        self.data[coordinates.YAW] = yaw

    @property
    def pitch(self):
        return self.data[coordinates.PITCH]

    @pitch.setter
    def pitch(self, pitch: float):
        self.data[coordinates.PITCH] = pitch

    @property
    def roll(self):
        return self.data[coordinates.ROLL]

    @roll.setter
    def roll(self, roll: float):
        self.data[coordinates.ROLL] = roll

    def rotate_point(self, point: PointCartesian) -> PointCartesian:
        x = point.x
        y = point.y
        z = point.z
        # Rotate around the x-axis
        x, y, z = (
            x,
            y * np.cos(self.yaw) - z * np.sin(self.yaw),
            y * np.sin(self.yaw) + z * np.cos(self.yaw),
        )
        # Rotate around the y-axis
        x, y, z = (
            x * np.cos(self.pitch) + z * np.sin(self.pitch),
            y,
            -x * np.sin(self.pitch) + z * np.cos(self.pitch),
        )
        # Rotate around the z-axis
        x, y, z = (
            x * np.cos(self.roll) - y * np.sin(self.roll),
            x * np.sin(self.roll) + y * np.cos(self.roll),
            z,
        )
        return PointCartesian(x, y, z)
