"""
draw_3d_eem.py — Draw 3D Excitation-Emission Matrix (EEM) plots from .TXT files.

Usage:
    python draw_3d_eem.py [options] <file1.txt> [file2.txt ...]

Options:
    -o, --output DIR     Directory to save output images (default: current dir)
    --cmap CMAP          Matplotlib colormap (default: jet)
    --vmax VMAX          Maximum intensity value for colour scale (auto if omitted)
    --contour            Draw 2-D filled-contour plot instead of 3-D surface
    --no-save            Show plots interactively and do not save to disk
    --dpi DPI            Resolution of saved images (default: 150)

Supported TXT format
--------------------
The first row must contain emission wavelengths (nm).
The first column must contain excitation wavelengths (nm).
The top-left cell may contain any label (e.g. "Ex/Em", "Ex\\Em", or be empty).
Values are separated by TABs or commas.

Example (tab-separated):
    Ex/Em   250  255  260  ...
    200     0.0  1.2  3.4  ...
    205     0.0  2.1  5.6  ...
    ...
"""

import argparse
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_eem_txt(filepath):
    """
    Load an EEM TXT file.

    Returns
    -------
    ex_wavelengths : 1-D ndarray  (n_ex,)
    em_wavelengths : 1-D ndarray  (n_em,)
    intensity      : 2-D ndarray  (n_ex, n_em)
    """
    with open(filepath, "r", encoding="utf-8-sig") as fh:
        raw = fh.read()

    # Auto-detect delimiter (tab or comma)
    delimiter = "\t" if "\t" in raw else ","

    lines = [line for line in raw.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError(f"File '{filepath}' has fewer than 2 non-empty lines.")

    # Parse emission wavelengths from header row (skip first cell)
    header_cells = lines[0].split(delimiter)
    em_wavelengths = np.array([float(v) for v in header_cells[1:] if v.strip()])

    # Parse excitation wavelengths and intensity matrix
    ex_list = []
    intensity_rows = []
    for line in lines[1:]:
        cells = line.split(delimiter)
        if not cells[0].strip():
            continue
        ex_list.append(float(cells[0]))
        intensity_rows.append([float(v) if v.strip() else 0.0
                                for v in cells[1:len(em_wavelengths) + 1]])

    ex_wavelengths = np.array(ex_list)
    intensity = np.array(intensity_rows)

    if intensity.shape != (len(ex_wavelengths), len(em_wavelengths)):
        raise ValueError(
            f"Shape mismatch in '{filepath}': "
            f"intensity {intensity.shape} vs "
            f"({len(ex_wavelengths)}, {len(em_wavelengths)})"
        )

    return ex_wavelengths, em_wavelengths, intensity


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------

def plot_3d_surface(ex, em, intensity, title, cmap="jet", vmax=None):
    """Return a matplotlib Figure with a 3-D surface EEM plot."""
    EM_grid, EX_grid = np.meshgrid(em, ex)

    vmin = 0.0
    if vmax is None:
        vmax = float(intensity.max())

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(
        EM_grid, EX_grid, intensity,
        cmap=cmap,
        vmin=vmin, vmax=vmax,
        linewidth=0,
        antialiased=True,
        rcount=100, ccount=100,
    )

    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label("Fluorescence Intensity (a.u.)", fontsize=10)

    ax.set_xlabel("Emission (nm)", fontsize=11, labelpad=10)
    ax.set_ylabel("Excitation (nm)", fontsize=11, labelpad=10)
    ax.set_zlabel("Intensity (a.u.)", fontsize=11, labelpad=10)
    ax.set_title(title, fontsize=13, pad=15)

    ax.view_init(elev=30, azim=-60)
    plt.tight_layout()
    return fig


def plot_contour(ex, em, intensity, title, cmap="jet", vmax=None, n_levels=20):
    """Return a matplotlib Figure with a 2-D filled-contour EEM plot."""
    vmin = 0.0
    if vmax is None:
        vmax = float(intensity.max())

    levels = np.linspace(vmin, vmax, n_levels + 1)

    fig, ax = plt.subplots(figsize=(9, 6))

    cf = ax.contourf(em, ex, intensity, levels=levels, cmap=cmap,
                     vmin=vmin, vmax=vmax)
    cs = ax.contour(em, ex, intensity, levels=levels, colors="k",
                    linewidths=0.3, alpha=0.4)

    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Fluorescence Intensity (a.u.)", fontsize=10)

    ax.set_xlabel("Emission (nm)", fontsize=12)
    ax.set_ylabel("Excitation (nm)", fontsize=12)
    ax.set_title(title, fontsize=13)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.tick_params(which="both", direction="in")

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Draw 3D / contour EEM plots from .TXT data files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("files", nargs="+", metavar="FILE",
                        help="One or more EEM .TXT files to process.")
    parser.add_argument("-o", "--output", default=".",
                        help="Directory to save output images (default: current dir).")
    parser.add_argument("--cmap", default="jet",
                        help="Matplotlib colormap name (default: jet).")
    parser.add_argument("--vmax", type=float, default=None,
                        help="Maximum intensity for colour scale (auto if omitted).")
    parser.add_argument("--contour", action="store_true",
                        help="Draw 2-D contour plot instead of 3-D surface.")
    parser.add_argument("--no-save", dest="no_save", action="store_true",
                        help="Show plots interactively instead of saving.")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Resolution of saved images (default: 150).")
    return parser.parse_args(argv)


def process_file(filepath, args):
    """Load one EEM file and produce its plot."""
    print(f"  Loading: {filepath}")
    ex, em, intensity = load_eem_txt(filepath)
    print(f"    Ex: {ex[0]:.0f}–{ex[-1]:.0f} nm  ({len(ex)} points)")
    print(f"    Em: {em[0]:.0f}–{em[-1]:.0f} nm  ({len(em)} points)")
    print(f"    Intensity range: {intensity.min():.1f} – {intensity.max():.1f}")

    base = os.path.splitext(os.path.basename(filepath))[0]
    title = base.replace("_", " ")

    if args.contour:
        fig = plot_contour(ex, em, intensity, title,
                           cmap=args.cmap, vmax=args.vmax)
        suffix = "_contour.png"
    else:
        fig = plot_3d_surface(ex, em, intensity, title,
                              cmap=args.cmap, vmax=args.vmax)
        suffix = "_3d.png"

    if args.no_save:
        plt.show()
    else:
        os.makedirs(args.output, exist_ok=True)
        out_path = os.path.join(args.output, base + suffix)
        fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
        print(f"    Saved → {out_path}")

    plt.close(fig)


def main(argv=None):
    args = parse_args(argv)

    # Select backend before any figure is created.
    # Use non-interactive Agg when saving to disk (the common case).
    if not args.no_save:
        matplotlib.use("Agg")
    errors = []
    for filepath in args.files:
        if not os.path.isfile(filepath):
            print(f"[WARNING] File not found, skipping: {filepath}", file=sys.stderr)
            continue
        try:
            process_file(filepath, args)
        except Exception as exc:
            print(f"[ERROR] {filepath}: {exc}", file=sys.stderr)
            errors.append(filepath)

    if errors:
        print(f"\n{len(errors)} file(s) failed to process.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
