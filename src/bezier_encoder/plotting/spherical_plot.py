import numpy as np
import plotly.graph_objects as go

from bezier_encoder.classes.points import PointCartesian


def generate_sphere_fig():
    u, v = np.mgrid[0 : 2 * np.pi : 50j, 0 : np.pi : 30j]
    sphere_x = np.cos(u) * np.sin(v)
    sphere_y = np.sin(u) * np.sin(v)
    sphere_z = np.cos(v)

    fig = go.Figure()
    fig.add_trace(go.Surface(x=sphere_x, y=sphere_y, z=sphere_z, opacity=0.3, showscale=False))
    fig.add_trace(go.Cone(x=[0], y=[0], z=[0], u=[0.4], v=[0], w=[0], showscale=False))
    # Format the layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(nticks=4, range=[-1, 1]),
            yaxis=dict(nticks=4, range=[-1, 1]),
            zaxis=dict(nticks=4, range=[-1, 1]),
        ),
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.25, y=1.25, z=1.25),
        ),
    )
    fig.update(
        layout_showlegend=False,
    )
    return fig


def add_points(
    fig: go.Figure, anchor_points: list[PointCartesian], control_points: list[PointCartesian]
):
    for i, anchor_point in enumerate(anchor_points):
        if i == 0:
            fig.add_trace(
                go.Scatter3d(
                    x=[anchor_point.x],
                    y=[anchor_point.y],
                    z=[anchor_point.z],
                    mode="markers",
                    marker=dict(size=5, color="red"),
                    name="Control Points",
                )
            )
        elif i == len(anchor_points) - 1:
            fig.add_trace(
                go.Scatter3d(
                    x=[anchor_point.x],
                    y=[anchor_point.y],
                    z=[anchor_point.z],
                    mode="markers",
                    marker=dict(size=5, color="green"),
                    name="Control Points",
                )
            )
        else:
            fig.add_trace(
                go.Scatter3d(
                    x=[anchor_point.x],
                    y=[anchor_point.y],
                    z=[anchor_point.z],
                    mode="markers",
                    marker=dict(size=5, color="black"),
                    name="Control Points",
                )
            )
    for control_point in control_points:
        fig.add_trace(
            go.Scatter3d(
                x=[control_point.x],
                y=[control_point.y],
                z=[control_point.z],
                mode="markers",
                marker=dict(size=5, color="blue"),
                name="Control Points",
            )
        )
    return fig


# def add_bezier_curve(fig: go.Figure, points: list[PointCartesian]) -> go.Figure:
#     for control_point in control_points:
#         fig.add_trace(
#             go.Scatter3d(
#                 x=[control_point.x],
#                 y=[control_point.y],
#                 z=[control_point.z],
#                 mode="markers",
#                 marker=dict(size=5, color="blue"),
#                 name="Control Points",
#             )
#         )
#     return fig
