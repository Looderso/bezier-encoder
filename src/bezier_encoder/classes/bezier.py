import numpy as np

import bezier_encoder.plotting.spherical_plot as spherical_plot
from bezier_encoder.classes.points import Point, Points, Rotation
from bezier_encoder.utils.spherical import slerp


class BezierCurve:
    def __init__(self, anchor_1: Point, anchor_2: Point, control: Point) -> None:
        self.anchor_1 = anchor_1
        self.anchor_2 = anchor_2
        self.control = control
        pass

    def get_point(self, t) -> Point:
        p1 = slerp(self.anchor_1, self.control, t)
        p2 = slerp(self.control, self.anchor_2, t)
        return slerp(p1, p2, t)

    # def get_points(self, t: np.ndarray | list[float]) -> Point:
    #     p1 = slerp(self.anchor_1, self.control, t)
    #     p2 = slerp(self.control, self.anchor_2, t)
    #     return slerp(p1, p2, t)


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

    def get_point(self, t: float) -> Point:
        bezier_index, t_bezier = self.get_sub_range(t)
        point = self.bezier_curves[bezier_index].get_point(t_bezier)
        return point

    def get_points(self, t: np.ndarray | list[float]) -> Points:
        points = Points.empty()
        for x in t:
            points.append(self.get_point(x))
        return points


class ModularBezierCurve:
    control_points: Points
    anchor_points: Points
    bezier_curve_collection: BezierCurveCollection

    def __init__(
        self,
        n_curves: int = 4,
        span: float = 360.0,
        plane_offset: float = 0,
        amplitude: float = 0.1,
        rotation: Rotation = Rotation(0, 0, 0),
    ):
        self._n_curves: int = n_curves
        self._span: float = span
        self._plane_offset: float = plane_offset
        self._amplitude: float = amplitude
        self._rotation: Rotation = rotation

        self.init_points()

    def init_points(self):
        total_span = np.deg2rad(self._span)
        plane_points_angles = np.linspace(
            -total_span / 2, total_span / 2, 2 * self._n_curves + 1, endpoint=True
        )
        plane_radius = np.cos(self._plane_offset)

        z_middle = np.sin(self._plane_offset)
        # theta_upper, theta_lower = np.clip(
        #     [
        #         self._plane_offset + self._amplitude - np.pi,
        #         self._plane_offset - self._amplitude + np.pi,
        #     ],
        #     -np.pi,
        #     np.pi,
        # )
        angular_amplitude = self.amplitude
        theta_upper = np.clip(self._plane_offset + angular_amplitude, -np.pi / 2, np.pi / 2)
        theta_lower = np.clip(self._plane_offset - angular_amplitude, -np.pi / 2, np.pi / 2)

        z_upper = np.sin(theta_upper)
        z_lower = np.sin(theta_lower)
        factor_upper = np.cos(theta_upper)
        factor_lower = np.cos(theta_lower)

        print(f"upper: {z_upper} middle: {z_middle} lower: {z_lower}")

        anchor_points = Points.empty()
        control_points = Points.empty()
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
                control_points.append_xyz(x, y, z)
            else:
                x *= plane_radius
                y *= plane_radius
                anchor_points.append_xyz(x, y, z_middle)

        self.anchor_points = self._rotation.rotate_points(anchor_points)
        self.control_points = self._rotation.rotate_points(control_points)
        self.bezier_curve_collection = self.accumulate_bezier_curves()

    def accumulate_bezier_curves(self) -> BezierCurveCollection:
        bezier_curves = []
        assert (
            self.anchor_points is not None and self.control_points is not None
        ), "Anchor points or control points are uninitialized"
        for i in range(self._n_curves):
            anchor_1 = self.anchor_points[i]
            anchor_2 = self.anchor_points[i + 1]
            control = self.control_points[i]
            bezier_curves.append(BezierCurve(anchor_1, anchor_2, control))  # type: ignore
        return BezierCurveCollection(bezier_curves)

    @property
    def n_curves(self):
        return self._n_curves

    @n_curves.setter
    def n_curves(self, n_curves: int):
        self._n_curves = n_curves
        self.init_points()

    @property
    def span(self):
        return self._span

    @span.setter
    def span(self, span: float):
        self._span = span
        self.init_points()

    @property
    def plane_offset(self):
        return self._plane_offset

    @plane_offset.setter
    def plane_offset(self, plane_offset: float):
        self._plane_offset = plane_offset
        self.init_points()

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amplitude: float):
        self._amplitude = amplitude
        self.init_points()
