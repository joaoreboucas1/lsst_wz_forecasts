"""
Script to compute cosmic shear scale cuts by iteratively removing data points that contribute the most to the chi2 between two input data vectors.
The script prints a mask file for Cocoa analyses, so the user can redirect that to a file of their preference.
Usage:
    python scale_cuts.py dv1 dv2 cov [threshold] [--output mask.txt]
Where:
    dv1: Path to first data vector (e.g. linear theory)
    dv2: Path to second data vector (e.g. halofit)
    cov: Path to covariance matrix
    threshold: Chi2 threshold for scale cuts (default: 1.0)
    --output: Output file for mask (default: mask.txt)
"""

from argparse import ArgumentParser
import os
import numpy as np

SHEAR_LEN = 780

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("dv1", type=str, help="Path to DV1 data vector")
    parser.add_argument("dv2", type=str, help="Path to DV2 data vector")
    parser.add_argument("cov", type=str, help="Path to covariance matrix")
    parser.add_argument("--threshold", type=float, default=1.0, help="Chi2 threshold for scale cuts")
    parser.add_argument("--output", type=str, default="mask.txt", help="Output file for mask (default: mask.txt)")
    args = parser.parse_args()

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

    if len(dv2) != len(dv1):
        print(f"Error: DV1 and DV2 have different lengths ({len(dv1)} vs {len(dv2)})")
        exit(1)

    print(f"Using shear-only data vector with {SHEAR_LEN} points")
    dv1 = dv1[:SHEAR_LEN]
    dv2 = dv2[:SHEAR_LEN]

    cov = np.zeros((SHEAR_LEN, SHEAR_LEN))

    with open(args.cov, "r") as f:
        for line in f.read().splitlines():
            words = line.split()
            i = int(words[0])
            j = int(words[1])
            if i >= SHEAR_LEN or j >= SHEAR_LEN: continue
            cov[i,j] = float(words[8]) + float(words[9])
            cov[j,i] = cov[i,j]

    delta = dv1 - dv2
    invcov = np.linalg.inv(cov)

    mask = np.ones_like(delta)
    chi2 = delta @ invcov @ delta
    threshold = args.threshold

    while chi2 > threshold:
        best_dchi2 = 0.0
        best_idx = None
        for idx in range(len(mask)):
            if mask[idx] == 0.0: continue

            trial_mask = mask.copy()
            trial_mask[idx] = 0.0
            
            masked_delta = delta*trial_mask
            
            chi2_trial = masked_delta @ invcov @ masked_delta
            dchi2_trial = chi2 - chi2_trial
            
            if dchi2_trial > best_dchi2:
                best_dchi2 = dchi2_trial
                best_idx = idx
        
        if best_idx is None:
            print("Could not find any improvement")
            break
        else:
            print(f"Removing data point #{best_idx} with chi2 reduction of {best_dchi2}")
            mask[best_idx] = 0.0
            masked_delta = delta*trial_mask
            chi2 = masked_delta @ invcov @ masked_delta
            print(f"New chi2 = {chi2}")

    print(f"Number of unmasked points in linear mask = {len(mask[mask > 0])}")
    print(f"chi2 between linear and halofit in linear mask = {chi2}")
    np.savetxt(args.output, np.vstack([np.arange(len(mask)), mask]).T, fmt="%d %d")