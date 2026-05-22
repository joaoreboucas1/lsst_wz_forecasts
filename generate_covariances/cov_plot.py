#!/usr/bin/env python3
"""Plot CosmoCov covariance products produced by ``cosmocov_process.py``.

By default this script uses the paths and bin counts in ``cosmocov_input.py``.
It expects these files:

* ``COSMOCOV/cov_<PROJECT_NAME>.txt``
* ``COSMOCOV/cov_<PROJECT_NAME>_g.txt``
* ``COSMOCOV/cov_<PROJECT_NAME>_corr.txt``

The plots are saved next to those files.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

import cosmocov_input as cfg


@dataclass(frozen=True)
class PlotConfig:
    project_name: str
    output_dir: Path
    ntheta: int
    n_source_bins: int
    n_lens_bins: int
    dpi: int

    @property
    def covariance_stem(self) -> Path:
        return self.output_dir / f"cov_{self.project_name}"

    @property
    def covariance_file(self) -> Path:
        return Path(f"{self.covariance_stem}.txt")

    @property
    def gaussian_covariance_file(self) -> Path:
        return Path(f"{self.covariance_stem}_g.txt")

    @property
    def correlation_file(self) -> Path:
        return Path(f"{self.covariance_stem}_corr.txt")


@dataclass(frozen=True)
class MatrixBlocks:
    xi_plus_end: int
    xi_minus_end: int
    gamma_t_end: int
    total_size: int


def matrix_blocks(config: PlotConfig, matrix_size: int) -> MatrixBlocks:
    """Return the index boundaries for xi+, xi-, gamma_t, and w(theta)."""
    n_source_pairs = config.n_source_bins * (config.n_source_bins + 1) // 2
    xi_plus_end = config.ntheta * n_source_pairs
    xi_minus_end = config.ntheta * config.n_source_bins * (config.n_source_bins + 1)
    gamma_t_end = config.ntheta * (
        config.n_source_bins * (config.n_source_bins + 1)
        + config.n_source_bins * config.n_lens_bins
    )
    return MatrixBlocks(
        xi_plus_end=xi_plus_end,
        xi_minus_end=xi_minus_end,
        gamma_t_end=gamma_t_end,
        total_size=matrix_size,
    )


def add_block_guides(ax: plt.Axes, blocks: MatrixBlocks) -> None:
    """Draw thick outer lines and thin data-vector block separators."""
    n = blocks.total_size
    for position in (-0.5, n - 0.5):
        ax.axvline(position, color="black", linewidth=2.0)
        ax.axhline(position, color="black", linewidth=2.0)

    for position in (
        blocks.xi_plus_end - 0.5,
        blocks.xi_minus_end - 0.5,
        blocks.gamma_t_end - 0.5,
    ):
        ax.axvline(position, color="black", linewidth=1.0)
        ax.axhline(position, color="black", linewidth=1.0)


def add_block_labels(ax: plt.Axes, blocks: MatrixBlocks) -> None:
    """Label the four 3x2pt data-vector sections."""
    starts = [0, blocks.xi_plus_end, blocks.xi_minus_end, blocks.gamma_t_end]
    ends = [
        blocks.xi_plus_end,
        blocks.xi_minus_end,
        blocks.gamma_t_end,
        blocks.total_size,
    ]
    labels = [
        r"$\xi_+^{ij}(\theta)$",
        r"$\xi_-^{ij}(\theta)$",
        r"$\gamma_t^{ij}(\theta)$",
        r"$w^i(\theta)$",
    ]
    centers = [(start + end) / 2 for start, end in zip(starts, ends)]

    ax.set_xticks(centers, labels=labels, rotation=30, ha="right")
    ax.set_yticks(centers, labels=labels)
    ax.tick_params(axis="both", labelsize=10)


def load_matrix(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"Missing matrix file: {path}")
    matrix = np.loadtxt(path)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Expected a square matrix in {path}, got shape {matrix.shape}")
    return matrix


def plot_matrix(
    matrix: np.ndarray,
    output_path: Path,
    blocks: MatrixBlocks,
    title: str,
    colorbar_label: str,
    cmap: str,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
    log_abs: bool = False,
    dpi: int = 300,
) -> None:
    """Save one covariance-style matrix plot."""
    figure, ax = plt.subplots(figsize=(8, 7), constrained_layout=True)

    image_data = np.abs(matrix) if log_abs else matrix
    if log_abs:
        image_data = np.ma.masked_less_equal(image_data, 0.0)
    norm = LogNorm() if log_abs else None
    image = ax.imshow(image_data, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax)

    add_block_guides(ax, blocks)
    add_block_labels(ax, blocks)
    ax.set_title(title)

    colorbar = figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label(colorbar_label)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=dpi)
    plt.close(figure)
    print(f"Saved {output_path}")


def plot_covariances(config: PlotConfig) -> None:
    """Load available covariance products and write standard diagnostic plots."""
    corr = load_matrix(config.correlation_file)
    blocks = matrix_blocks(config, corr.shape[0])

    plot_matrix(
        corr,
        Path(f"{config.covariance_stem}_corr_plot.pdf"),
        blocks,
        "Correlation matrix",
        r"$r_{ij}$",
        "seismic",
        vmin=-1,
        vmax=1,
        dpi=config.dpi,
    )

    cov_g = load_matrix(config.gaussian_covariance_file)
    plot_matrix(
        cov_g,
        Path(f"{config.covariance_stem}_g_plot.pdf"),
        blocks,
        "Gaussian covariance matrix",
        r"$|\mathrm{Cov}_{G}|$",
        "viridis",
        log_abs=True,
        dpi=config.dpi,
    )

    cov = load_matrix(config.covariance_file)
    plot_matrix(
        cov,
        Path(f"{config.covariance_stem}_cov_plot.pdf"),
        blocks,
        "Total covariance matrix",
        r"$|\mathrm{Cov}|$",
        "viridis",
        log_abs=True,
        dpi=config.dpi,
    )


def parse_args() -> PlotConfig:
    parser = argparse.ArgumentParser(description="Plot CosmoCov covariance matrices.")
    parser.add_argument("--project-name", default=cfg.PROJECT_NAME)
    parser.add_argument("--output-dir", type=Path, default=cfg.OUTPUT_DIR)
    parser.add_argument("--ntheta", type=int, default=20)
    parser.add_argument("--n-source-bins", type=int, default=cfg.N_BIN_SOURCE)
    parser.add_argument("--n-lens-bins", type=int, default=cfg.N_BIN_LENS)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    return PlotConfig(
        project_name=args.project_name,
        output_dir=args.output_dir,
        ntheta=args.ntheta,
        n_source_bins=args.n_source_bins,
        n_lens_bins=args.n_lens_bins,
        dpi=args.dpi,
    )


def main() -> None:
    plot_covariances(parse_args())


if __name__ == "__main__":
    main()
