# LSST w(z) forecasts

This project uses Cocoa to make forecasts for smooth dark energy models using LSST 3x2pt data.

> [!Important]
> If you find any bugs in this project, please contact João or Diogo ASAP!

## Contents

- `data/` contains all necessary ingredients to perform a 3x2pt analysis with LSST Y1 and Y10: $n(z)$ for sources and lenses, covariance matrices, model data vectors, and `.dataset` files for Cocoa.
- `generate_covariances/` contains necessary ingredients to compute the covariance matrices for LSST Y1 and Y10 using CosmoCov.
- `sn/` contains files for LSST supernovae.
- `sh/` contains SLURM scripts for running chains.
- `yamls/` contains `.yaml` files for running Cocoa.
- `modifications/` contains modifications to the `lsst_y1` Cocoa project so users can run Y10 chains.

## Testing CoCoA Legacy, Stable and Beta  

### Legacy Version - branch v4.052: 
OK  
### Stable Version - branch v4.071  
OK  
### Beta Release - branch v4.11.2   
OK

LSST SN: covariances taken from https://zenodo.org/records/1409816  
How to use in CoCoA: copy sn/sn_lsst_like/ to cocoa/Cocoa/cobaya/cobaya/likelihoods/  
Examples: yamls/EXAMPLE_SN_EVALUATE_Y1.yaml for year 1 and yamls/EXAMPLE_SN_EVALUATE_Y10.yaml for year 10  
