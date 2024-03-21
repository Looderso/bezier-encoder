import bezier_encoder.plotting.spherical_plot as spherical_plot
import dash
import dash_mantine_components as dmc
import numpy as np
from bezier_encoder.classes.bezier import ModularBezierCurve
from bezier_encoder.classes.points import Rotation
from dash import callback_context, dcc, html
from dash.dependencies import Input, Output

mbc = ModularBezierCurve(4, 270, 0, 0.1, Rotation(0, 0, 0))

# Initialize the Dash app
app = dash.Dash(__name__)

t_curve = np.linspace(0, 1, 100)
fig = spherical_plot.generate_sphere_fig()
fig = spherical_plot.update_points(fig, mbc.anchor_points, mbc.control_points)  # type: ignore
fig = spherical_plot.update_point(fig, mbc.bezier_curve_collection.get_point(0.0))
fig = spherical_plot.update_curve(fig, mbc.bezier_curve_collection.get_points(t_curve))
# Define the layout of the app
app.layout = dmc.Group(
    [
        dcc.Graph(id="graph", figure=fig),
        dmc.Stack(
            [
                html.Div(
                    [
                        "Curves",
                        dmc.Slider(id="slider_n_curves", min=2, max=16, step=1, value=4),
                    ]
                ),
                html.Div(
                    [
                        "Span",
                        dmc.Slider(id="slider_span", min=10, max=360, step=5, value=270),
                    ]
                ),
                html.Div(
                    [
                        "Plane Offset",
                        dmc.Slider(
                            id="slider_plane_offset",
                            min=-np.pi / 2,
                            max=np.pi / 2,
                            step=0.1,
                            value=0,
                        ),
                    ]
                ),
                html.Div(
                    [
                        "Amplitude",
                        dmc.Slider(id="slider_amplitude", min=0, max=np.pi / 2, step=0.1, value=0),
                    ]
                ),
                html.Div(
                    [
                        "Position",
                        dmc.Slider(id="slider_t", min=0, max=1, step=0.01, value=0),
                    ]
                ),
            ]
        ),
    ],
    grow=True,
)


# Callback to update the plot based on slider inputs
@app.callback(
    [
        Output("graph", "figure"),
        Input("slider_n_curves", "value"),
        Input("slider_span", "value"),
        Input("slider_plane_offset", "value"),
        Input("slider_amplitude", "value"),
        Input("slider_t", "value"),
    ],
    prevent_initial_call=True,
)
def update_figure(n_curves, span, plane_offset, amplitude, t):
    match callback_context.triggered_id:
        case "slider_n_curves":
            mbc.n_curves = n_curves
        case "slider_span":
            mbc.span = span
        case "slider_plane_offset":
            mbc.plane_offset = plane_offset
        case "slider_amplitude":
            mbc.amplitude = amplitude
    fig = spherical_plot.generate_sphere_fig()
    fig = spherical_plot.update_points(fig, mbc.anchor_points, mbc.control_points)  # type: ignore
    fig = spherical_plot.update_point(fig, mbc.bezier_curve_collection.get_point(t))
    fig = spherical_plot.update_curve(fig, mbc.bezier_curve_collection.get_points(t_curve))
    return (fig,)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
