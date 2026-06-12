# Cocoa LSST-Y1 Pipeline Modifications

This project uses the [Cocoa LSST-Y1](https://github.com/CosmoLike/cocoa_lsst_y1) project as a baseline for running both Y1 and Y10 chains. However, Y10 chains have a different number of lens bins (10, compared to 5 in Y1), and thus Cobaya needs to know about the extra nuisance parameters for the additional bins 6-10. This is automatically done by introducing additional parameters in the `params_lens.yaml` file.

To run Y10 chains, just copy `params_lens.yaml` into your `Cocoa/projects/lsst_y1/likelihood` folder. A backup of the original file is recommended.

The nuisance parameters for bins 6-10 are set to zero by default. Their priors must be explicitly set in Y10 `.yaml` files.