#!/usr/bin/env python3
"""Run CosmoCov, collect its block outputs, and save dense covariance matrices.

This script is intentionally only the CosmoCov part of the older pipeline:

1. Read run settings from ``cosmocov_input.py``.
2. Run every CosmoCov block with ``PATH_COSMOCOV_REPO/covs/cov``.
3. Concatenate ``COSMOCOV/out_cov*`` into ``COSMOCOV/cov_<PROJECT_NAME>``.
4. Save dense covariance, Gaussian covariance, and correlation matrices.

The CosmoCov physics/survey settings stay in ``comsocov.ini``. Values that
CosmoCov does not read directly, such as the repository path and worker count,
stay in ``cosmocov_input.py``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
from pathlib import Path

import numpy as np

import cosmocov_input as cfg


def covariance_block_count(n_source_bins: int, n_lens_bins: int) -> int:
    """Return the number of independent covariance blocks for this 3x2pt setup."""
    n_columns = n_lens_bins + n_source_bins * n_lens_bins
    n_columns += n_source_bins * (n_source_bins + 1)
    return n_columns * (n_columns + 1) // 2


def run_block(block: int, cov_executable: Path, ini_file: Path) -> tuple[int, str, str]:
    """Run one CosmoCov block and return its captured output."""
    result = subprocess.run(
        [str(cov_executable), str(block), str(ini_file)],
        check=False,
        capture_output=True,
        cwd=cfg.BASE_DIR,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"CosmoCov block {block} failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return block, result.stdout, result.stderr


def run_all_blocks(max_workers: int | None = None) -> None:
    """Run all CosmoCov blocks in parallel."""
    cov_executable = cfg.PATH_COSMOCOV_REPO / "covs" / "cov"
    if not cov_executable.exists():
        raise FileNotFoundError(f"CosmoCov executable not found: {cov_executable}")
    if not cfg.INI_FILE.exists():
        raise FileNotFoundError(f"CosmoCov ini not found: {cfg.INI_FILE}")

    cfg.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    n_blocks = covariance_block_count(cfg.N_BIN_SOURCE, cfg.N_BIN_LENS)
    workers = max_workers or cfg.MAX_WORKERS

    print(f"Running {n_blocks} CosmoCov blocks with {workers} workers")
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(run_block, block, cov_executable, cfg.INI_FILE)
            for block in range(1, n_blocks + 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            block, stdout, stderr = future.result()
            print(f"Block {block} complete")
            if stdout.strip():
                print(stdout, end="" if stdout.endswith("\n") else "\n")
            if stderr.strip():
                print(stderr, end="" if stderr.endswith("\n") else "\n")


def collect_block_files() -> Path:
    """Concatenate CosmoCov's block files into one sparse covariance text file."""
    block_files = sorted(cfg.OUTPUT_DIR.glob(f"{cfg.OUTPUT_STEM}*"))
    if not block_files:
        raise FileNotFoundError(
            f"No block files found matching {cfg.OUTPUT_DIR / (cfg.OUTPUT_STEM + '*')}"
        )

    collected_file = cfg.OUTPUT_DIR / cfg.FINAL_COVARIANCE_STEM
    with collected_file.open("w") as destination:
        for block_file in block_files:
            with block_file.open() as source:
                destination.writelines(source)
    return collected_file


def build_matrices(collected_file: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert the sparse CosmoCov text output into dense matrix products."""
    data = np.loadtxt(collected_file)
    ndata = int(np.max(data[:, 0])) + 1

    cov_g = np.zeros((ndata, ndata))
    cov_ng = np.zeros((ndata, ndata))
    for row in data:
        i = int(row[0])
        j = int(row[1])
        cov_g[i, j] = cov_g[j, i] = row[8]
        cov_ng[i, j] = cov_ng[j, i] = row[9]

    cov = cov_g + cov_ng
    diagonal = np.sqrt(np.outer(np.diag(cov), np.diag(cov)))
    corr = np.divide(cov, diagonal, out=np.zeros_like(cov), where=diagonal != 0)
    return cov_g, cov, corr


def save_outputs(collected_file: Path) -> None:
    """Save dense covariance products and fail if the covariance is invalid."""
    cov_g, cov, corr = build_matrices(collected_file)

    eigenvalues = np.linalg.eigvalsh(cov)
    print(f"Dimension of cov: {cov.shape[0]}x{cov.shape[1]}")
    print(f"min+max eigenvalues cov: {np.min(eigenvalues):e}, {np.max(eigenvalues):e}")
    if np.min(eigenvalues) <= 0.0:
        raise ValueError("non-positive eigenvalue encountered; covariance invalid")
    print("Covariance is positive definite")

    np.savetxt(f"{collected_file}.txt", cov)
    np.savetxt(f"{collected_file}_g.txt", cov_g)
    np.savetxt(f"{collected_file}_corr.txt", corr)
    print(f"Saved covariance outputs with stem {collected_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run CosmoCov blocks and collect them into covariance matrices."
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=[1, 10],
        help="LSST Year (1 or 10).",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Skip CosmoCov execution and only collect existing block files.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel CosmoCov workers. Defaults to cosmocov_input.MAX_WORKERS.",
    )
    args = parser.parse_args()
    
    if args.year == 1:
        cfg.PROJECT_NAME = cfg.PROJECT_NAME_Y1
        cfg.INI_FILE = cfg.INI_FILE_Y1
        cfg.OUTPUT_STEM = cfg.OUTPUT_STEM_Y1
        cfg.FINAL_COVARIANCE_STEM = cfg.FINAL_COVARIANCE_STEM_Y1
        cfg.N_BIN_SOURCE = cfg.N_BIN_SOURCE_Y1
        cfg.N_BIN_LENS = cfg.N_BIN_LENS_Y1
    else:
        cfg.PROJECT_NAME = cfg.PROJECT_NAME_Y10
        cfg.INI_FILE = cfg.INI_FILE_Y10
        cfg.OUTPUT_STEM = cfg.OUTPUT_STEM_Y10
        cfg.FINAL_COVARIANCE_STEM = cfg.FINAL_COVARIANCE_STEM_Y10
        cfg.N_BIN_SOURCE = cfg.N_BIN_SOURCE_Y10
        cfg.N_BIN_LENS = cfg.N_BIN_LENS_Y10


    if not args.skip_run:
        run_all_blocks(args.workers)
    collected_file = collect_block_files()
    save_outputs(collected_file)


if __name__ == "__main__":
    main()
