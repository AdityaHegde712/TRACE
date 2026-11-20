"""Shared look for the preprint figures: one palette, one font size, PDF + PNG output.

Colors are the Okabe-Ito set, checked with the dataviz palette validator. Two
slots sit in its CVD floor band, so every series also differs in marker shape
and is labeled directly or in a legend; color is never the only cue.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

FIGURES_DIR = Path(__file__).resolve().parents[1] / "paper" / "figures"

INK = "#222222"
MUTED = "#6b6b6b"
GRID = "#d9d9d9"
BLUE = "#0072B2"
VERMILLION = "#D55E00"
GREEN = "#009E73"
PINK = "#CC79A7"
ORANGE = "#E69F00"
SKY = "#56B4E9"

COLUMN_WIDTH_IN = 3.4
PAGE_WIDTH_IN = 7.0


def apply_style() -> None:
    """Set matplotlib defaults for a two-column paper: small, legible, quiet grid."""
    import matplotlib

    # These scripts only write files. An interactive backend would need a display
    # and a working Tk install, and fails on machines without them.
    matplotlib.use("Agg")
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.5,
            "axes.axisbelow": True,
            "legend.frameon": False,
            "pdf.fonttype": 42,  # embed TrueType so fonts stay editable and searchable
            "ps.fonttype": 42,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def save_figure(fig: Any, stem: Path | str) -> list[Path]:
    """Write `<stem>.pdf` and `<stem>.png`, creating the folder if needed."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix in ("pdf", "png"):
        path = Path(f"{stem}.{suffix}")
        fig.savefig(path)
        written.append(path)
    return written
