from __future__ import annotations

import os
import tempfile

import imageio
import numpy as np
import plotly.graph_objects as go


# %%
def animate_frames(
    frames: list[go.Frame],
    duration: float = 100,
    **kwargs,
) -> go.Figure:
    """Animate frames.

    Args:
        frames (list[go.Frame]): Frames to animate.
        duration (float, optional): Duration of each frame in ms. Defaults to 100.
        **kwargs: Passed to `go.Figure.update_layout`.

    Returns:
        go.Figure: Animation.
    """
    for idx, frame in enumerate(frames):
        frame.name = str(idx)

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=frames[0].layout,
    )

    fig.update_layout(
        margin={"l": 50, "r": 0, "t": 0, "b": 150},
        yaxis={"scaleanchor": "x", "scaleratio": 1},
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {
                                    "duration": duration,
                                    "redraw": True,
                                },
                                "fromcurrent": True,
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "steps": [
                    {
                        "method": "animate",
                        "args": [
                            [str(idx)],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": True,
                                },
                                "mode": "immediate",
                            },
                        ],
                        "label": str(idx),
                    }
                    for idx in range(len(frames))
                ],
                "currentvalue": {"prefix": "Frame "},
            }
        ],
        **kwargs,
    )

    return fig


def plot_data_frames(
    data: np.ndarray,
    colorscale: str = "Viridis",
) -> list[go.Heatmap]:
    """Create plots for each frame of a dataset.

    Args:
        data (np.ndarray): Data to plot, indexed by `(frame, x, y)`.
        colorscale (str, optional): Color scale. Defaults to "Viridis".

    Returns:
        list[go.Heatmap]: Heatmap of each frame.
    """
    frames = [
        go.Heatmap(
            z=data[frame, :, :],
            colorscale=colorscale,
            colorbar=None,
            zauto=False,
            zmin=0,
            zmax=1,
        )
        for frame in range(data.shape[0])
    ]

    return frames


def animate(
    df: np.ndarray,
    speed: float = 1,
    scale: float = 1,
    colorscale: str = "Viridis",
) -> go.Figure:
    """Animate a Hypercube.

    Args:
        cube (Hypercube): Data to visualize.
        speed (float, optional): Playback speed. Defaults to 1.
        scale (float, optional): Plot scale. Defaults to 1.
        colorscale (str, optional): Color scale. Defaults to "Viridis".

    Returns:
        go.Figure: Animation.
    """
    plots = plot_data_frames(
        df,
        colorscale=colorscale,
    )

    annotations = [str(f) for f in range(len(df))]
    annotations_frame = [
        [
            {
                "text": text,
                "xref": "paper",
                "yref": "paper",
                "x": 0.02,
                "y": 0.05,
                "showarrow": False,
                "font": {"size": 16, "color": "white"},
            }
        ]
        for text in annotations
    ]

    scene = {
        "xaxis_title": "X",
        "yaxis_title": "Y",
        "zaxis_title": "Intensity",
    }

    frames = [
        go.Frame(
            data=[plot],
            layout=go.Layout(annotations=annotations_frame[idx]),
        )
        for idx, plot in enumerate(plots)
    ]

    duration = float(len(df) * speed)
    return animate_frames(
        frames,
        duration=duration,
        scene=scene,
    )


def figs_to_gif(
    out: os.PathLike,
    frames: list[go.Figure],
    duration: int = 100,
):
    """Create a gif.

    Args:
        out (os.PathLike): Output path.
        frames (list[go.Figure]): Frames.
        duration (float, optional): Frame duration in ms. Defaults to 100.
        progress (bool, optional): Print progress. Defaults to False.
    """
    imgs = []
    for idx, fig in enumerate(frames):
        with tempfile.NamedTemporaryFile(delete_on_close=False) as tmp:
            fig.write_image(tmp.name, format="png")
            tmp.close()
            img = imageio.v3.imread(tmp.name)
            imgs.append(img)

    out_str = str(out)
    _, ext = os.path.splitext(out)
    if ext != ".gif":
        out_str = out_str + ".gif"

    imageio.v3.imwrite(out_str, imgs, extension=".gif", duration=duration)


def to_gif(
    df: np.ndarray,
    out: os.PathLike,
    duration: int = 100,
    scale: float = 1,
    colorscale: str = "Viridis",
):
    """Save a cube as a gif.

    Args:
        cube (Hypercube): Data to visualize.
        out (os.PathLike): Output path.
        duration (float, optional): Frame duration in ms. Defaults to 100.
        scale (float, optional): Plot scale. Defaults to 1.
        colorscale (str, optional): Color scale. Defaults to "Viridis".
    """
    plots = plot_data_frames(df, colorscale=colorscale)
    annotations_frame = [
        [
            {
                "text": str(frame),
                "xref": "paper",
                "yref": "paper",
                "x": 0.02,
                "y": 0.05,
                "showarrow": False,
                "font": {"size": 16, "color": "white"},
            }
        ]
        for frame in range(len(df))
    ]

    scene = {
        "xaxis_title": "X",
        "yaxis_title": "Y",
        "zaxis_title": "Intensity",
    }

    frames = [
        go.Figure(
            data=[plot],
            layout=go.Layout(
                annotations=annotations_frame[idx],
                yaxis={"scaleanchor": "x", "scaleratio": 1},
                scene=scene,
            ),
        )
        for idx, plot in enumerate(plots)
    ]

    figs_to_gif(
        out,
        frames,
        duration=duration,
    )
