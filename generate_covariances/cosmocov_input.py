"""Configuration for ``cosmocov_process.py``.

Keep only runner/metaparameters here: paths, output names, bin counts, and
parallelism. The actual CosmoCov parameters are kept in ``comsocov.ini`` so the
ini can still be passed directly to ``covs/cov``.
"""

from pathlib import Path

# Directory containing this small three-file CosmoCov setup.
BASE_DIR = Path(__file__).resolve().parent


# Path to the CosmoCov checkout. The runner expects the executable at:
#   PATH_COSMOCOV_REPO / "covs" / "cov"
PATH_COSMOCOV_REPO = Path("/home/u3/joaoreboucas/CosmoCov")

# Main files/directories used by the runner.
OUTPUT_DIR = BASE_DIR / "CosmoCov_output"

PROJECT_NAME_Y1 = "LSST_Y1"
INI_FILE_Y1 = BASE_DIR / "lsst_y1_cov.ini"
OUTPUT_STEM_Y1 = "lsst_y1_cov"
FINAL_COVARIANCE_STEM_Y1 = f"lsst_y1_cov"
N_BIN_SOURCE_Y1 = 5
N_BIN_LENS_Y1 = 5

PROJECT_NAME_Y10 = "LSST_Y10"
INI_FILE_Y10 = BASE_DIR / "lsst_y10_cov.ini"
OUTPUT_STEM_Y10 = "lsst_y10_cov"
FINAL_COVARIANCE_STEM_Y10 = f"lsst_y10_cov"
N_BIN_SOURCE_Y10 = 5
N_BIN_LENS_Y10 = 10


# Number of CosmoCov blocks to run at once.
MAX_WORKERS = 32

# Optional pipeline metadata from the old setup. These are not used by
# cosmocov_process.py, but are left here as documentation for the run.
# REDSHIFT_BINS_SOURCE = [0.01, 0.41, 0.59, 0.81, 1.3]
# REDSHIFT_BINS_LENS = [0.0, 0.2, 0.4, 0.6, 0.8]

# SCALE_CUTS_XI_PLUS_INF = [
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
# ]
# SCALE_CUTS_XI_PLUS_SUP = [
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
# ]
# SCALE_CUTS_XI_MINUS_INF = [
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
# ]
# SCALE_CUTS_XI_MINUS_SUP = [
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
#     [100.0, 100.0, 100.0, 100.0],
# ]
# SCALE_CUTS_GAMMA_T_INF = [
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
#     [10.0, 10.0, 10.0, 10.0],
# ]
# SCALE_CUTS_W_INF = [10.0, 10.0, 10.0, 10.0]
