import numpy as np

import bezier_encoder.plotting.spherical_plot as spherical_plot
from bezier_encoder.classes.points import PointCartesian, Rotation
from bezier_encoder.utils.spherical import slerp


class BezierCurve:
    def __init__(
        self, anchor_1: PointCartesian, anchor_2: PointCartesian, control: PointCartesian
    ) -> None:
        self.anchor_1 = anchor_1
        self.anchor_2 = anchor_2
        self.control = control
        pass

    def get_point(self, t) -> PointCartesian:
        p1 = slerp(self.anchor_1, self.control, t)
        p2 = slerp(self.control, self.anchor_2, t)
        return slerp(p1, p2, t)


class BezierCurveCollection:
    def __init__(self, bezier_curves: list[BezierCurve]):
        self.bezier_curves = bezier_curves
        self.n_bezier_curves = len(self.bezier_curves)

    def get_sub_range(self, t: float):
        assert 0 <= t <= 1, "t must be between 0 and 1."
        # Length of each subrange
        subrange_length = 1 / self.n_bezier_curves

        # Determine the index of the subrange where t falls
        if t == 1:
            subrange_index = self.n_bezier_curves - 1
            position_within_subrange = 1.0
        else:
            # Determine the index of the subrange where t falls
            subrange_index = int(t // subrange_length)

            # Calculate the position of t within the found subrange, normalized to [0, 1]
            position_within_subrange = (t % subrange_length) / subrange_length

        return subrange_index, position_within_subrange

    def get_point(self, t: float) -> PointCartesian:
        bezier_index, t_bezier = self.get_sub_range(t)
        point = self.bezier_curves[bezier_index].get_point(t_bezier)
        return point


class ModularBezierCurve:
    def __init__(
        self,
        n_curves: int = 4,
        span: float = 360.0,
        plane_offset: float = 0,
        amplitude: float = 0.1,
        rotation: Rotation = Rotation(0, 0, 0),
    ):
        self.n_curves: int = n_curves
        self.span: float = span
        self.plane_offset: float = plane_offset
        self.amplitude: float = amplitude
        self.rotation: Rotation = rotation
        self.control_points: list[PointCartesian] | None = None
        self.anchor_points: list[PointCartesian] | None = None
        self.bezier_curve_collection: BezierCurveCollection | None = None
        self.init_points()

    def init_points(self):
        total_span = np.deg2rad(self.span)
        plane_points_angles = np.linspace(
            -total_span / 2, total_span / 2, 2 * self.n_curves + 1, endpoint=True
        )
        plane_radius = np.cos(self.plane_offset)
        anchor_points = []
        control_points = []
        self.amplitude
        theta_upper, theta_lower = np.clip(
            [self.plane_offset + self.amplitude, self.plane_offset - self.amplitude], 0, np.pi
        )

        z_middle = np.sin(self.plane_offset)
        z_upper = np.cos(theta_upper)
        z_lower = np.cos(theta_lower)
        factor_upper = np.sin(theta_upper)
        factor_lower = np.sin(theta_lower)
        # radius_factor_upper =
        for i, phi in enumerate(plane_points_angles):
            x = np.cos(phi)
            y = np.sin(phi)
            if i % 2 == 1:
                if (i // 2) % 2 == 0:
                    x *= factor_upper
                    y *= factor_upper
                    z = z_upper
                else:
                    x *= factor_lower
                    y *= factor_lower
                    z = z_lower
                # z = np.sin(self.plane_offset) + self.amplitude * ((-1) ** ((i // 2) % 2))
                control_points.append(PointCartesian(x, y, z))
            else:
                x *= plane_radius
                y *= plane_radius
                anchor_points.append(PointCartesian(x, y, z_middle))

        self.control_points = self.rotate_points(control_points)
        self.anchor_points = self.rotate_points(anchor_points)
        self.bezier_curve_collection = self.accumulate_bezier_curves(anchor_points, control_points)
        pass

    def rotate_points(self, points: list[PointCartesian]):
        # TODO move me to rotation class, make it work on point collection with a single data member
        # for efficiency -> ROTATION GOES BRRRRR
        for point in points:
            point = self.rotation.rotate_point(point)
        return points

    def accumulate_bezier_curves(
        self, anchor_points: list[PointCartesian], control_points: list[PointCartesian]
    ) -> BezierCurveCollection:
        bezier_curves = []
        for i in range(self.n_curves):
            anchor_1 = anchor_points[i]
            anchor_2 = anchor_points[i + 1]
            control = control_points[i]
            bezier_curves.append(BezierCurve(anchor_1, anchor_2, control))
        return BezierCurveCollection(bezier_curves)
