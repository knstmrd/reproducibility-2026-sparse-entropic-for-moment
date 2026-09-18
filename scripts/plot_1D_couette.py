#!/usr/bin/env python
"""
Plot couette flow output

Produces a 2x2 figure at a chosen snapshot, overlaying one line per input file:
    1: density                    -- the (0,0,0) moment
    2: y-velocity                 -- (0,1,0) / density
    3: temperature                -- (2/3) * thermal energy from the 2nd moments
    4: <given moment> / density   -- the moment order passed on the command line

--xmin/--xmax restrict the plot to a physical x range; the nearest cell centers
inside that range are used (the range is not a cell-index range).
The plot assumes that the moment being plotted is the 1,1,0 one

Example:
    python plot_1D_couette.py --files a.h5 b.h5 --labels "upwind" "upwind_lw" \\
        --moment 1,1,0 --timestep -1 --length 1.0 --xmin 0.0 --xmax 1.0 \\
        --colors black tab:red --linestyles solid dashed \\
        --output sod.png

--colors and --linestyles are optional; when given they need one entry per file.
Omitting --colors falls back to the matplotlib color cycle, omitting
--linestyles to solid lines. Spell the styles out (solid, dashed, dashdot,
dotted) rather than using '--' or '-.', which argparse would read as options.
"""

import argparse

import h5py
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# set plotting parameters
label_size = 24
tick_size = 20
legend_size = 20

plt.rcParams["text.usetex"] = True
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Computer Modern Roman"]
plt.rcParams["axes.linewidth"] = 0.8

def parse_moment(s):
    """'1,2,1' -> (1, 2, 1)."""
    parts = [int(p) for p in s.replace(" ", "").split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"moment must be 'a,b,c', got {s!r}")
    return tuple(parts)


def find_row(powers, target):
    """Row index of moment power `target` (a,b,c) in the (m,3) powers array."""
    for i, p in enumerate(powers):
        if tuple(int(v) for v in p) == tuple(target):
            return i
    raise ValueError(f"moment {tuple(target)} not present in file")


def read_snapshot(path, timestep):
    """Return (powers (m,3), snapshot (n_cells, m), time, step) at `timestep`."""
    with h5py.File(path, "r") as f:
        powers = f["moment_powers"][...]          # (m, 3)
        moments = f["moments"]                     # (n_snap, n_cells, m)
        n_snap = moments.shape[0]
        if not (-n_snap <= timestep < n_snap):
            raise IndexError(
                f"{path}: timestep {timestep} out of range (n_snapshots={n_snap})"
            )
        snap = moments[timestep, :, :]             # (n_cells, m)
        time = float(f["times"][timestep])
        step = int(f["steps"][timestep])
    return powers, snap, time, step


def derived_fields(powers, snap, moment):
    """Compute (density, uy, temperature, moment/density) profiles for one file."""
    col = lambda a, b, c: snap[:, find_row(powers, (a, b, c))]

    rho = col(0, 0, 0)
    ux, uy, uz = col(1, 0, 0) / rho, col(0, 1, 0) / rho, col(0, 0, 1) / rho

    # thermal energy <c^2> = <v^2> - u^2, then T = (2/3) * energy
    energy = (col(2, 0, 0) + col(0, 2, 0) + col(0, 0, 2)) / rho - (ux**2 + uy**2 + uz**2)
    temperature = (2.0 / 3.0) * energy

    single = col(*moment) #/ rho
    return rho, uy, temperature, single


def range_mask(x, xmin, xmax):
    """Boolean mask of cell centers within [xmin, xmax], snapped to nearest cells.

    If no center falls strictly inside the range (a range narrower than a cell,
    or one lying between two centers), the single nearest center is kept.
    """
    mask = (x >= xmin) & (x <= xmax)
    if not mask.any():
        mask = np.zeros_like(x, dtype=bool)
        mask[np.argmin(np.abs(x - 0.5 * (xmin + xmax)))] = True
    return mask


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", nargs="+", required=True, help="HDF5 output files")
    ap.add_argument("--labels", nargs="+", required=True, help="legend label per file")
    ap.add_argument("--moment", type=parse_moment, required=True,
                    help="moment order for subplot 4, e.g. '1,2,1'")
    ap.add_argument("--timestep", type=int, required=True,
                    help="snapshot index (0-based; negatives count from the end)")
    ap.add_argument("--length", type=float, required=True, help="domain length")
    ap.add_argument("--xmin", type=float, default=None,
                    help="lower physical x bound to plot (default: 0)")
    ap.add_argument("--xmax", type=float, default=None,
                    help="upper physical x bound to plot (default: domain length)")
    ap.add_argument("--colors", nargs="*", default=[],
                    help="line color per file (default: matplotlib color cycle)")
    ap.add_argument("--linestyles", nargs="*", default=[],
                    help="line style per file: solid, dashed, dashdot, dotted "
                         "(default: solid)")
    ap.add_argument("--titletext", type=str, default=None, help="additional text to add to title")
    ap.add_argument("--output", default="plot_1d_sod.png", help="output image path")
    args = ap.parse_args()

    print(args.labels)

    if len(args.files) != len(args.labels):
        ap.error(f"got {len(args.files)} files but {len(args.labels)} labels")
    if args.colors and len(args.colors) != len(args.files):
        ap.error(f"got {len(args.files)} files but {len(args.colors)} colors")
    if args.linestyles and len(args.linestyles) != len(args.files):
        ap.error(f"got {len(args.files)} files but {len(args.linestyles)} linestyles")

    xmin = 0.0 if args.xmin is None else args.xmin
    xmax = args.length if args.xmax is None else args.xmax
    if xmin >= xmax:
        ap.error(f"--xmin ({xmin}) must be below --xmax ({xmax})")

    a, b, c = args.moment
    fig, axes = plt.subplots(2, 2, figsize=(20, 12), sharex=True)
    ax_rho, ax_uy, ax_T, ax_m = axes.flat

    times = []
    x_lo, x_hi = np.inf, -np.inf
    for i, (path, label) in enumerate(zip(args.files, args.labels)):
        # empty --colors keeps the matplotlib cycle; empty --linestyles keeps solid lines
        style = {"linewidth": 2.0, "linestyle": args.linestyles[i] if args.linestyles else "-"}
        if args.colors:
            style["color"] = args.colors[i]

        powers, snap, time, step = read_snapshot(path, args.timestep)
        times.append(time)

        n_cells = snap.shape[0]
        dx = args.length / n_cells
        x = (np.arange(n_cells) + 0.5) * dx      # cell centers

        rho, uy, T, single = derived_fields(powers, snap, args.moment)

        m = range_mask(x, xmin, xmax)
        x_lo, x_hi = min(x_lo, x[m][0]), max(x_hi, x[m][-1])

        ax_rho.plot(x[m], rho[m], label=rf"{label}", **style)
        ax_uy.plot(x[m], uy[m], label=rf"{label}", **style)
        ax_T.plot(x[m], T[m], label=rf"{label}", **style)
        ax_m.plot(x[m], single[m], label=rf"{label}", **style)

    ax_rho.set_title("Density", fontsize=label_size)
    ax_rho.set_ylabel(r"$\rho$", fontsize=label_size)
    ax_uy.set_title("$y$-velocity", fontsize=label_size)
    ax_uy.set_ylabel(r"$u_y$", fontsize=label_size)
    ax_T.set_title("Temperature", fontsize=label_size)
    ax_T.set_ylabel(r"$T$", fontsize=label_size)

    # m_abc_str = r"$M_{" + f"{a}{b}{c}" + r"} / \rho$" 
    m_abc_str = r"$M_{" + f"{a}{b}{c}" + r"}$" 
    ax_m.set_title(rf"Shear stress", fontsize=label_size)
    ax_m.set_ylabel(m_abc_str, fontsize=label_size)
    for ax in (ax_T, ax_m):
        ax.set_xlabel("$x$", fontsize=label_size)
    for ax in axes.flat:
        if x_hi > x_lo:   # a single retained cell leaves the limits to matplotlib
            ax.set_xlim(x_lo, x_hi)
            ax.grid(linewidth=0.4)
            ax.tick_params(axis='both', labelsize=tick_size)

    ax_rho.legend(fontsize=legend_size, framealpha=1.0)   # legend on the first subplot only

    # t_txt = f"$t$ = {times[0]:.4g}" if len(set(f"{t:.6g}" for t in times)) == 1 \
    #     else f"snapshot {args.timestep}"
    fig.suptitle(f"Couette flow", fontsize=label_size)
    fig.tight_layout()
    # fig.savefig(args.output, dpi=130)
    fig.savefig(args.output, bbox_inches="tight")
    print(f"wrote {args.output}")

if __name__ == "__main__":
    main()
