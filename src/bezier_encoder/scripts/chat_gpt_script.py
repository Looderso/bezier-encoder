import numpy as np
import plotly.graph_objects as go


# Convert polar to cartesian coordinates
def polar_to_cartesian(theta, phi):
    return np.array([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)])


# Convert back from cartesian to polar coordinates
def cartesian_to_polar(x, y, z):
    phi = np.arccos(z)
    theta = np.arctan2(y, x)
    return theta, phi


def slerp(p0, p1, t):
    """Perform spherical linear interpolation between two points on a sphere."""
    # Convert points from polar to cartesian coordinates
    v0 = polar_to_cartesian(*p0)
    v1 = polar_to_cartesian(*p1)

    # Compute the cosine of the angle between the vectors
    dot = np.dot(v0, v1)
    # Avoid a division by zero
    if dot > 0.9995:
        return cartesian_to_polar(*(v0 + t * (v1 - v0)))

    # Compute the actual angle
    theta = np.arccos(dot)
    sin_theta = np.sin(theta)

    # Compute the spherical linear interpolation
    s0 = np.sin((1 - t) * theta) / sin_theta
    s1 = np.sin(t * theta) / sin_theta
    v2 = s0 * v0 + s1 * v1

    # Convert back to polar coordinates
    return cartesian_to_polar(*v2)


def bezier_spherical(p0, p1, p2, t):
    """Calculate the Bezier point for a given parameter t on a spherical surface."""
    # Calculate the two intermediate points
    q0 = slerp(p0, p1, t)
    q1 = slerp(p1, p2, t)
    # Calculate the final Bezier point
    return slerp(q0, q1, t)


# Convert spherical coordinates to Cartesian for plotting
def spherical_to_cartesian(theta, phi):
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    return x, y, z


def generate_control_points(
    n, plane_offset=np.pi / 4, rotation_angles=(0, 0, 0), peak_amplitude=0.5
):
    """Generate sets of control points for Bezier curves that form a continuous, smooth path.

    :param n: The number of Bezier curves (segments).
    :param plane_offset: Offset from the equatorial plane (affects the latitude of the base line).
    :param rotation_angles: Rotation of the entire set of points around x, y, and z axes.
    :param peak_amplitude: The amplitude of the peaks from the central plane.
    """
    # The total number of unique points is 2n (for n segments, considering continuity)
    angles = np.linspace(0, 2 * np.pi, 2 * n + 1, endpoint=False)  # +1 because it's circular
    control_points = []

    for i, angle in enumerate(angles):
        # Base radius for control points
        radius = np.cos(plane_offset)

        # Peaks alternate sides; odd i for one side, even i for the other
        if i % 2 == 1:
            # Peaks (control points that dictate the direction of the curve)
            z = np.sin(plane_offset) + peak_amplitude * (
                (-1) ** ((i // 2) % 2)
            )  # Alternate peaks up and down
        else:
            # Troughs or base points (they lie on the initial plane)
            z = np.sin(plane_offset)

        # Compute the initial (unrotated) x and y coordinates
        x = np.cos(angle) * radius
        y = np.sin(angle) * radius

        # Apply the rotations around each axis
        # Rotate around the x-axis
        x, y, z = (
            x,
            y * np.cos(rotation_angles[0]) - z * np.sin(rotation_angles[0]),
            y * np.sin(rotation_angles[0]) + z * np.cos(rotation_angles[0]),
        )
        # Rotate around the y-axis
        x, y, z = (
            x * np.cos(rotation_angles[1]) + z * np.sin(rotation_angles[1]),
            y,
            -x * np.sin(rotation_angles[1]) + z * np.cos(rotation_angles[1]),
        )
        # Rotate around the z-axis
        x, y, z = (
            x * np.cos(rotation_angles[2]) - y * np.sin(rotation_angles[2]),
            x * np.sin(rotation_angles[2]) + y * np.cos(rotation_angles[2]),
            z,
        )

        # Convert back to spherical coordinates
        theta = np.arctan2(y, x)
        phi = np.arccos(z / np.sqrt(x**2 + y**2 + z**2))

        control_points.append((theta, phi))

    return control_points


def create_closed_bezier_curve(control_points, t_values):
    """Create a closed Bezier curve composed of n segments."""
    points = []
    n = len(control_points) // 2  # Number of Bezier curves
    for i in range(n):
        # Define control points for the i-th Bezier curve
        p0 = control_points[2 * i % (2 * n)]
        p1 = control_points[(2 * i + 1) % (2 * n)]
        p2 = control_points[(2 * i + 2) % (2 * n)]
        # Generate points on the i-th Bezier curve
        bezier_points = [bezier_spherical(p0, p1, p2, t) for t in t_values]
        points.extend(bezier_points)
    return points


# Number of Bezier curves to form the closed loop
n = 4  # Feel free to change this as needed

# Generate control points
control_points = generate_control_points(n, 0, (0, 0, 0))

# Generate points on the closed Bezier curve
t_values = np.linspace(0, 1, 25)  # Adjust the density of points as needed
closed_curve_points = create_closed_bezier_curve(control_points, t_values)
curve_x, curve_y, curve_z = zip(
    *[spherical_to_cartesian(theta, phi) for theta, phi in closed_curve_points]
)

# Add the sphere
u, v = np.mgrid[0 : 2 * np.pi : 20j, 0 : np.pi : 10j]
sphere_x = np.cos(u) * np.sin(v)
sphere_y = np.sin(u) * np.sin(v)
sphere_z = np.cos(v)

# Create a plot
fig = go.Figure()

# Add the sphere to the plot
fig.add_trace(go.Surface(x=sphere_x, y=sphere_y, z=sphere_z, opacity=0.3, colorscale="Blues"))

# Add closed Bezier curve
fig.add_trace(
    go.Scatter3d(
        x=curve_x,
        y=curve_y,
        z=curve_z,
        mode="lines",
        line=dict(color="red", width=4),
        name="Closed Bezier Curve",
    )
)

# Add control points
ctrl_pts_x, ctrl_pts_y, ctrl_pts_z = zip(
    *[spherical_to_cartesian(theta, phi) for theta, phi in control_points]
)
fig.add_trace(
    go.Scatter3d(
        x=ctrl_pts_x,
        y=ctrl_pts_y,
        z=ctrl_pts_z,
        mode="markers",
        marker=dict(size=5, color="black"),
        name="Control Points",
    )
)

# Format the layout
fig.update_layout(
    title=f"3D Spherical Closed Bezier Curve with {n} Segments",
    scene=dict(
        xaxis=dict(nticks=4, range=[-1, 1], backgroundcolor="rgb(200, 200, 230)"),
        yaxis=dict(nticks=4, range=[-1, 1], backgroundcolor="rgb(230, 200,230)"),
        zaxis=dict(nticks=4, range=[-1, 1], backgroundcolor="rgb(230, 230,200)"),
    ),
    scene_camera=dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.25, y=1.25, z=1.25),
    ),
)

# fig.write_html("bezier.html", auto_open=True)
fig.show()
# print()
