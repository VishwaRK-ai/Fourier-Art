import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


from src.image_processing.edges import extract_contours
from src.geometry.stitch import stitch_contours
from src.Fourier.signal import (
    to_complex_signal,
    resample_by_arclength,
    fourier_coefficients,
)
from src.Fourier.epicycles import epicycles_positions


def render_epicycle_animation(
    image_path,
    output_path = "output.gif",
    num_samples=3000,
    K=100,
    frames = 600,
):
    #logic
    contours = extract_contours(image_path)
    points = stitch_contours(contours)

    z = to_complex_signal(points)
    z = z - np.mean(z)
    z = z / np.max(np.abs(z))
    z = resample_by_arclength(z, num_samples=num_samples)

    coeffs, freqs = fourier_coefficients(z)
    K = min(K, len(coeffs))

    #matplot setup
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    circle_artists = []
    line_artists = []

    for _ in range(K):
        circle = plt.Circle((0, 0), 0, fill=False, alpha=0.4)
        ax.add_artist(circle)
        circle_artists.append(circle)

        line, = ax.plot([], [], "k-", lw=1)
        line_artists.append(line)

    trace_line, = ax.plot([], [], "r-", lw=2)
    trace = []


    def update(frame):
        t = frame / frames
        centers, ends = epicycles_positions(coeffs, freqs, t, K)

        for i, (c, e) in enumerate(zip(centers, ends)):
            r = abs(e - c)
            circle_artists[i].center = (c.real, -c.imag)
            circle_artists[i].radius = r

            line_artists[i].set_data(
                [c.real, e.real],
                [-c.imag, -e.imag],
            )

        tip = ends[-1]
        trace.append(tip)

        xs = [p.real for p in trace]
        ys = [-p.imag for p in trace]
        trace_line.set_data(xs, ys)

        return circle_artists + line_artists + [trace_line]

    ani = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=20,
        blit=True,
    )

    ani.save(output_path, writer="pillow", fps=30)
    plt.close(fig)