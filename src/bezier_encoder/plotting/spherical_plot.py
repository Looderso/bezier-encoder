import numpy as np
import plotly.graph_objects as go

from bezier_encoder.classes.points import Point, Points


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
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update(
        layout_showlegend=False,
    )
    return fig


def update_points(fig: go.Figure, a_points: Points, c_points: Points) -> go.Figure:
    for i in range(a_points.num_points):
        if i == 0:
            fig.add_trace(
                go.Scatter3d(
                    x=[a_points.x[i]],
                    y=[a_points.y[i]],
                    z=[a_points.z[i]],
                    mode="markers",
                    marker=dict(size=5, color="red"),
                    name="anchor_start",
                )
            )
        elif i == a_points.num_points - 1:
            fig.add_trace(
                go.Scatter3d(
                    x=[a_points.x[i]],
                    y=[a_points.y[i]],
                    z=[a_points.z[i]],
                    mode="markers",
                    marker=dict(size=5, color="green"),
                    name="anchor",
                )
            )
        else:
            fig.add_trace(
                go.Scatter3d(
                    x=[a_points.x[i]],
                    y=[a_points.y[i]],
                    z=[a_points.z[i]],
                    mode="markers",
                    marker=dict(size=5, color="black"),
                    name="anchor_end",
                )
            )
    for i in range(c_points.num_points):
        fig.add_trace(
            go.Scatter3d(
                x=[c_points.x[i]],
                y=[c_points.y[i]],
                z=[c_points.z[i]],
                mode="markers",
                marker=dict(size=5, color="blue"),
                name="control",
            )
        )
    return fig


def update_point(fig: go.Figure, point: Point) -> go.Figure:
    fig.add_trace(
        go.Scatter3d(
            x=[point.x],
            y=[point.y],
            z=[point.z],
            mode="markers",
            marker=dict(size=10, color="orange"),
            name="direction",
        )
    )
    return fig


def update_curve(fig: go.Figure, points: Points) -> go.Figure:
    fig.add_trace(
        go.Scatter3d(
            x=points.x,
            y=points.y,
            z=points.z,
            mode="lines",
            line=dict(color="red", width=4),
            name="curve",
        )
    )
    return fig
