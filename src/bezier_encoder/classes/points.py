from __future__ import annotations

import numpy as np

import bezier_encoder.classes.coordinates as coordinates
import bezier_encoder.utils.lin_alg as lin_alg


class Point:
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

    def dot(self, other: Point) -> float:
        return np.sum(self.data * other.data)  # type: ignore

    def __add__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Point.from_data(self.data + other.data)
        return Point.from_data(self.data + other)

    def __sub__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Point.from_data(self.data - other.data)
        return Point.from_data(self.data - other)

    def __mul__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Point.from_data(self.data * other.data)
        return Point.from_data(self.data * other)

    def __truediv__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Point.from_data(self.data / other.data)
        return Point.from_data(self.data / other)

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

    def to_cartesian(self) -> Point:
        return Point.from_polar(self.phi, self.theta, self.r)


class Points:
    def __init__(self, data: np.ndarray):
        assert data.ndim == 2
        assert data.shape[1] == 3
        self.data = data

    @classmethod
    def from_xyz(
        cls,
        x: np.ndarray | list[float],
        y: np.ndarray | list[float],
        z: np.ndarray | list[float],
    ):
        return cls(np.array([x, y, z]).T)

    @classmethod
    def from_list(cls, points: list[Point]):
        return cls(np.array([p.data for p in points]))

    @classmethod
    def empty(cls):
        return cls(np.array([], dtype=np.float64).reshape(0, 3))

    def append(self, point: Point):
        self.data = np.concatenate([self.data, point.data[np.newaxis, :]])

    def append_xyz(self, x: float, y: float, z: float):
        self.data = np.concatenate([self.data, np.array([x, y, z])[np.newaxis, :]])

    @property
    def x(self):
        return self.data[:, coordinates.X]

    @property
    def y(self):
        return self.data[:, coordinates.Y]

    @property
    def z(self):
        return self.data[:, coordinates.Z]

    @property
    def num_points(self):
        return self.data.shape[0]

    def dot(self, other: Point | Points) -> np.ndarray:
        if isinstance(other, Points):
            assert self.data.shape == other.data.shape
        return np.sum(self.data * other.data, axis=-1)  # type: ignore

    def __add__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Points(self.data + other.data)
        return Points(self.data + other)

    def __sub__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Points(self.data - other.data)
        return Points(self.data - other)

    def __mul__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Points(self.data * other.data)
        return Points(self.data * other)

    def __truediv__(self, other: Point | float | int):
        if isinstance(other, Point):
            return Points(self.data / other.data)
        return Points(self.data / other)

    def __getitem__(self, key) -> Point | Points:
        if isinstance(key, slice):
            n_entries = len(range(*key.indices(self.num_points)))
        elif isinstance(key, int):
            n_entries = 1
        else:
            raise KeyError(
                "invalid Key. Only integers and slices are supported and "
                "only the first dimension can be indexed."
            )

        ret = self.data[key]
        if n_entries == 1:
            return Point.from_data(ret.squeeze())
        elif n_entries == 0:
            return Points.empty()
        else:
            return Points(ret)


class Rotation:
    def __init__(self, yaw: float, pitch: float, roll: float) -> None:
        self.data = np.array([yaw, pitch, roll])
        self.rot_mat = self.create_rotation_matrix()

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

    def create_rotation_matrix(self):
        rz = np.array(
            [
                [np.cos(self.yaw), -np.sin(self.yaw), 0],
                [np.sin(self.yaw), np.cos(self.yaw), 0],
                [0, 0, 1],
            ]
        )
        ry = np.array(
            [
                [np.cos(self.pitch), 0, np.sin(self.pitch)],
                [0, 1, 0],
                [-np.sin(self.pitch), 0, np.cos(self.pitch)],
            ]
        )
        rx = np.array(
            [
                [1, 0, 0],
                [0, np.cos(self.roll), -np.sin(self.roll)],
                [0, np.sin(self.roll), np.cos(self.roll)],
            ]
        )
        rot_mat = rz @ ry @ rx
        return rot_mat

    def rotate_point(self, point: Point) -> Point:
        x = float(point.x)
        y = float(point.y)
        z = float(point.z)
        # Rotate around the z-axis
        x, y = (
            x * np.cos(self.roll) - y * np.sin(self.roll),
            x * np.sin(self.roll) + y * np.cos(self.roll),
        )
        # Rotate around the y-axis
        x, z = (
            x * np.cos(self.pitch) + z * np.sin(self.pitch),
            -x * np.sin(self.pitch) + z * np.cos(self.pitch),
        )
        # Rotate around the x-axis
        y, z = (
            y * np.cos(self.yaw) - z * np.sin(self.yaw),
            y * np.sin(self.yaw) + z * np.cos(self.yaw),
        )

        return Point(x, y, z)

    def rotate_points(self, points: Points):
        return Points(points.data @ self.rot_mat)
