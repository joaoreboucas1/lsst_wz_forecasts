r"""
Script to compute scale cuts using DES-Y3 methodology (Krause et al 2021):
- Cosmic shear cuts are determined by finding a values for \theta_min in each pair of bins (i, j) such that, for every bin pair, \Delta\chi^2_(i,j) in that specific bin it less than \Delta\chi^2_threshold / NUM_SHEAR_2PCFS. The \Delta\chi^2 is the difference between a data vector computed with a fiducial model (e.g. no baryonic feedback) and a data vector computed with a model that has a small-scale modification (e.g. baryonic feedback). \Delta\chi^2_threshold is an user input and NUM_SHEAR_2PCFS is equal to 30 (15 xi_plus and 15 xi_minus) for 5 source bins.
- Clustering and GGL scale cuts are detemined by setting minimum separation scales in Mpc/h, and then converting those to minimum angular separations using the average redshift of each lens bin.
The script prints a mask file for Cocoa analyses, so the user can redirect that to a file of their preference.
Usage:
    python scale_cuts.py dv1 dv2 cov [--chi2_threshold threshold] [--Rmin_gc Rmin_gc] [--Rmin_ggl Rmin_ggl] [--output mask_filename]
Where:
    dv1: Path to first data vector (e.g. linear theory)
    dv2: Path to second data vector (e.g. halofit)
    cov: Path to covariance matrix
    threshold: Chi2 threshold for cosmic shear scale cuts (default: 1.0)
    Rmin_gc: Minimum separation scale for galaxy clustering in Mpc/h (default: 1.0)
    Rmin_ggl: Minimum separation scale for galaxy-galaxy lensing in Mpc/h (default: 1.0)
    mask_filename: Output file for mask (default: mask.txt)
"""

from argparse import ArgumentParser
from astropy.cosmology import FlatLambdaCDM
import os
import numpy as np
import itertools

SHEAR_LEN = 780
NUM_SRC_BINS = 5
NUM_SHEAR_2PCFS = 30 # 5 bins -> 15 xip and 15 xim
NUM_LENS_BINS_Y1 = 5
NUM_LENS_BINS_Y10 = 10

ARCMIN_TO_RAD = 2.90888208665721580e-4
RAD_TO_ARCMIN = 1/ARCMIN_TO_RAD
THETA_MIN_ARCMIN  = 2.5   # Minimum angular scale (in arcminutes)
THETA_MAX_ARCMIN  = 900.  # Maximum angular scale (in arcminutes)
NUM_ANG_BINS = 26    # Number of angular bins

THETA_MIN_RAD = THETA_MIN_ARCMIN * ARCMIN_TO_RAD
THETA_MAX_RAD = THETA_MAX_ARCMIN * ARCMIN_TO_RAD
DLOG_THETA = (np.log(THETA_MAX_RAD) - np.log(THETA_MIN_RAD))/NUM_ANG_BINS
theta = np.zeros(NUM_ANG_BINS)

LENS_Z_MEANS_Y1  = (0.317, 0.505, 0.700, 0.896, 1.093)
LENS_Z_MEANS_Y10 = (0.263, 0.358, 0.456, 0.555, 0.653, 0.752, 0.851, 0.950, 1.049, 1.149)

for i in range(NUM_ANG_BINS):
    THETA_MIN_BIN = np.exp(np.log(THETA_MIN_RAD) + i * DLOG_THETA)
    THETA_MAX_BIN = np.exp(np.log(THETA_MIN_RAD) + (i + 1) * DLOG_THETA)
    theta[i] = (2/3) * (THETA_MAX_BIN**3 - THETA_MIN_BIN**3) / (THETA_MAX_BIN**2 - THETA_MIN_BIN**2)

theta *= RAD_TO_ARCMIN

def make_pairs(max_i):
    pairs = []
    for i in range(1, max_i+1):
        for j in range(i, max_i+1):
            pairs.append((i, j))
    return pairs

pairs = make_pairs(5)   # enough to cover k up to 14


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("dv1", type=str, help="Path to DV1 data vector")
    parser.add_argument("dv2", type=str, help="Path to DV2 data vector")
    parser.add_argument("cov", type=str, help="Path to covariance matrix")
    parser.add_argument("--year", type=int, required=True, choices=(1, 10), help="LSST Observation Year (choices: 1 or 10)")
    parser.add_argument("--threshold", type=float, default=0.5, help="Chi2 threshold for cosmic shear scale cuts (default: 0.5)")
    parser.add_argument("--Rmin_gc",   type=float, default=8.0, help="Minimum separation scale for galaxy clustering in Mpc/h (default: 8)")
    parser.add_argument("--Rmin_ggl",  type=float, default=6.0, help="Minimum separation scale for galaxy-galaxy lensing in Mpc/h (default: 6)")
    parser.add_argument("--output", type=str, default="mask.txt", help="Output file for mask (default: mask.txt)")
    parser.add_argument("--verbose", action="store_true", help="Enable tracing of shear scale cuts")
    args = parser.parse_args()

    if args.year == 1:
        NUM_LENS_BINS = NUM_LENS_BINS_Y1
        LENS_Z_MEANS = LENS_Z_MEANS_Y1
    elif args.year == 10:
        NUM_LENS_BINS = NUM_LENS_BINS_Y10
        LENS_Z_MEANS = LENS_Z_MEANS_Y10
    else:
        print(f"Error: invalid LSST year {args.year}")
        exit(1)

    if not os.path.exists(args.dv1):
        print(f"Error: {args.dv1} does not exist")
        exit(1)
    if not os.path.exists(args.dv2):
        print(f"Error: {args.dv2} does not exist")
        exit(1)
    if not os.path.exists(args.cov):
        print(f"Error: {args.cov} does not exist")
        exit(1)
    
    _, dv1 = np.loadtxt(args.dv1, unpack=True)
    _, dv2 = np.loadtxt(args.dv2, unpack=True)

    dv_length = len(dv1)
    if len(dv2) != dv_length:
        print(f"Error: DV1 and DV2 have different lengths ({dv_length} vs {len(dv2)})")
        exit(1)

    # Shear part of data vectors for dchi2 calculations
    dv1 = dv1[:SHEAR_LEN]
    dv2 = dv2[:SHEAR_LEN]
    dv_length = SHEAR_LEN

    cov = np.zeros((dv_length, dv_length))

    with open(args.cov, "r") as f:
        for line in f.read().splitlines():
            if line.startswith("#"): continue
            words = line.split()
            i = int(words[0])
            j = int(words[1])
            if i >= dv_length or j >= dv_length: continue
            cov[i,j] = float(words[8]) + float(words[9])
            cov[j,i] = cov[i,j]

    # Cosmic shear scale cuts
    delta = dv1 - dv2
    invcov = np.linalg.inv(cov)

    mask = np.ones_like(delta)

    threshold = args.threshold

    def compute_cuts_xi_ij():
        minimum_angles = np.zeros((NUM_SHEAR_2PCFS,))
        full_shear_mask = np.empty(0)
        for i in range(NUM_SHEAR_2PCFS):
            shear_func = "xi_plus" if i < NUM_SHEAR_2PCFS//2 else "xi_minus"
            bin_pair = pairs[i%(NUM_SHEAR_2PCFS//2)]

            mask = np.ones((NUM_ANG_BINS,))
            num_removed_elements = 0
            idx_start = i * NUM_ANG_BINS
            idx_end = (i + 1) * NUM_ANG_BINS
            delta_ij = delta[idx_start:idx_end].copy()
            invcov_ij = invcov[idx_start:idx_end, idx_start:idx_end]
            chi2_ij = delta_ij @ invcov_ij @ delta_ij
            if args.verbose:
                print("--------------------")
                print(f"Initial chi2 for {shear_func} bin pair {bin_pair} = {chi2_ij}")
            while chi2_ij > args.threshold / NUM_SHEAR_2PCFS:
                mask[num_removed_elements] = 0.0
                num_removed_elements += 1
                delta_ij_masked = delta_ij * mask
                chi2_ij = delta_ij_masked @ invcov_ij @ delta_ij_masked
                if args.verbose: print(f"After removing {num_removed_elements} elements, chi2 for {shear_func} bin pair {bin_pair} = {chi2_ij}")
            full_shear_mask = np.concatenate((full_shear_mask, mask))
            minimum_angles[i] = theta[num_removed_elements]
        return minimum_angles, full_shear_mask

    min_angles, shear_mask = compute_cuts_xi_ij()
    print("Minimum angles for shear 2pcfs:")
    for i, (pair, min_angle) in enumerate(zip(itertools.cycle(pairs), min_angles)):
        shear_func = "xi_plus" if i < NUM_SHEAR_2PCFS//2 else "xi_minus"
        print(f"  - {shear_func} {pair}: {min_angle:.1f}")
    print(f"Original number of elements: {len(shear_mask)}, number of unmasked elements: {len(shear_mask[shear_mask > 0])}")
    print("--------------------")
    
    def compute_cuts_gc_ggl():
        theta_mins_gc = []
        theta_mins_ggl = []
        cosmo = FlatLambdaCDM(H0=67, Om0=0.319)
        full_gc_mask = np.empty(0)
        full_ggl_mask = np.empty(0)

        for i in range(NUM_LENS_BINS):
            z_mean = LENS_Z_MEANS[i]
            comoving_dist = cosmo.angular_diameter_distance(z_mean).value
            theta_min_gc  = args.Rmin_gc / comoving_dist * RAD_TO_ARCMIN
            theta_min_ggl = args.Rmin_ggl / comoving_dist * RAD_TO_ARCMIN
            theta_mins_gc.append(round(theta_min_gc, 2))
            theta_mins_ggl.append(round(theta_min_ggl, 2))
            gc_mask = theta > theta_min_gc
            ggl_mask = theta > theta_min_ggl
            full_gc_mask = np.concatenate((full_gc_mask, gc_mask))
            for j in range(NUM_SRC_BINS): full_ggl_mask = np.concatenate((full_ggl_mask, ggl_mask))

        return full_gc_mask, theta_mins_gc, full_ggl_mask, theta_mins_ggl

    gc_mask, theta_mins_gc, ggl_mask, theta_mins_ggl = compute_cuts_gc_ggl()
    print(f"GGL minimum angles: {theta_mins_ggl}")
    print(f"Original number of elements: {len(ggl_mask)}, number of unmasked elements: {len(ggl_mask[ggl_mask > 0])}")
    print("--------------------")
    print(f"GC minimum angles: {theta_mins_gc}")
    print(f"Original number of elements: {len(gc_mask)}, number of unmasked elements: {len(gc_mask[gc_mask > 0])}")
    print("--------------------")

    full_mask = np.concatenate((shear_mask, ggl_mask, gc_mask))
    print(f"Number of unmasked points in mask = {len(full_mask[full_mask > 0])} out of {len(full_mask)}")

    np.savetxt(args.output, np.vstack([np.arange(len(full_mask)), full_mask]).T, fmt="%d %d")
    print(f"Saved mask in {args.output}")