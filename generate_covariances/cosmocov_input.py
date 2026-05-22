"""Configuration for ``cosmocov_process.py``.

Keep only runner/metaparameters here: paths, output names, bin counts, and
parallelism. The actual CosmoCov parameters are kept in ``comsocov.ini`` so the
ini can still be passed directly to ``covs/cov``.
"""

from pathlib import Path

# Directory containing this small three-file CosmoCov setup.
BASE_DIR = Path(__file__).resolve().parent

PROJECT_NAME = "LSST"

# Path to the CosmoCov checkout. The runner expects the executable at:
#   PATH_COSMOCOV_REPO / "covs" / "cov"
PATH_COSMOCOV_REPO = Path("/home/joao/cosmo/CosmoCov")

# Main files/directories used by the runner.
INI_FILE = BASE_DIR / "roman_cov.ini"
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_STEM = "roman_cov"
FINAL_COVARIANCE_STEM = f"roman_cov"

# These must match source_tomobins/lens_tomobins in comsocov.ini.
N_BIN_SOURCE = 8
N_BIN_LENS = 8

# Number of CosmoCov blocks to run at once.
MAX_WORKERS = 24

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
