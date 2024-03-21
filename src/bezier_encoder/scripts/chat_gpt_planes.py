import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Sphere parameters
R = 10  # Radius of the sphere

# Define the layout of the app
app.layout = html.Div(
    [
        html.H1("Interactive Sphere and Planes"),
        dcc.Graph(id="sphere-planes-plot"),
        html.Label(
            [
                "Central Plane Theta (Radians):",
                dcc.Slider(id="theta-slider", min=0, max=np.pi / 2, step=0.01, value=0),
            ]
        ),
        html.Label(
            [
                "Amplitude (Distance):",
                dcc.Slider(id="amplitude-slider", min=0, max=10, step=0.1, value=5),
            ]
        ),
    ]
)


# Callback to update the plot based on slider inputs
@app.callback(
    Output("sphere-planes-plot", "figure"),
    [Input("theta-slider", "value"), Input("amplitude-slider", "value")],
)
def update_figure(theta_center, amplitude):
    # Generate the updated figure using the provided function
    fig = create_sphere_and_planes(theta_center, amplitude, R)
    return fig


# Function to create the 3D plot
def create_sphere_and_planes(theta_center, amplitude, R):
    # Sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = R * np.outer(np.cos(u), np.sin(v))
    y = R * np.outer(np.sin(u), np.sin(v))
    z = R * np.outer(np.ones(np.size(u)), np.cos(v))

    # Planes
    theta_upper = max(min(theta_center + amplitude, np.pi / 2), -np.pi / 2)
    theta_lower = max(min(theta_center - amplitude, np.pi / 2), -np.pi / 2)
    z_center = R * np.cos(theta_center)
    z_upper = R * np.cos(theta_upper)
    z_lower = R * np.cos(theta_lower)

    plane_x, plane_y = np.meshgrid(np.linspace(-R, R, 2), np.linspace(-R, R, 2))
    plane_z_center = z_center * np.ones(plane_x.shape)
    plane_z_upper = z_upper * np.ones(plane_x.shape)
    plane_z_lower = z_lower * np.ones(plane_x.shape)

    # Plotting
    fig = go.Figure(
        data=[
            go.Surface(z=z, x=x, y=y, colorscale="Blues", opacity=0.5),
            go.Surface(z=plane_z_center, x=plane_x, y=plane_y, showscale=False, opacity=0.5),
            go.Surface(
                z=plane_z_upper,
                x=plane_x,
                y=plane_y,
                showscale=False,
                opacity=0.5,
                colorscale="Greens",
            ),
            go.Surface(
                z=plane_z_lower,
                x=plane_x,
                y=plane_y,
                showscale=False,
                opacity=0.5,
                colorscale="Reds",
            ),
        ]
    )

    fig.update_layout(
        title="Sphere with Three Planes", autosize=True, margin=dict(l=65, r=50, b=65, t=90)
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
