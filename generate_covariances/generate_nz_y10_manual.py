import numpy as np

def smail(z, z0=0.11, beta=2, alpha=0.68, zmin=None, zmax=None):
    z = np.asarray(z)
    nz = z**beta * np.exp(-(z / z0)**alpha)
    if zmax is not None:
        nz = np.where(z <= zmax, nz, 0.0)
    if zmin is not None:
        nz = np.where(z >= zmin, nz, 0.0)
    return nz / np.trapezoid(nz, z)

if __name__ == "__main__":
    samples = {
        "source": (5,  0.11, 0.68, 0, 3.5, 0.05),
        "lens":   (10, 0.283, 0.900, 0.2, 1.2, 0.05),
    }

    for sample, (num_bins, z0, alpha, zmin, zmax, sigma_gauss_conv) in samples.items():
        z = np.linspace(0.0, 3.5, 1000)
        nz = smail(z, z0=z0, alpha=alpha, zmin=zmin, zmax=zmax)  # normalized to unity
        dz = z[1] - z[0]
        cum = np.cumsum(nz) * dz

        # bin edges that split the distribution into equal-number bins
        quantiles = np.linspace(0.0, 1.0, num_bins + 1)
        z_edges = np.interp(quantiles, cum, z)

        # overall mean
        mean_z = np.trapezoid(z * nz, z)

        binned_nz_list = []
        for i in range(num_bins):
            z0_edge = z_edges[i]
            z1_edge = z_edges[i + 1]
            mask = (z >= z0_edge) & (z <= z1_edge)
            nz_bin = np.where(mask, nz, 0.0)
            area = np.trapezoid(nz_bin, z)
            if area > 0:
                nz_bin_norm = nz_bin / area
            else:
                nz_bin_norm = nz_bin

            # Convolve the binned distribution with a Gaussian kernel 
            hw = max(1, int(np.ceil(5 * sigma_gauss_conv / dz)))
            kernel_x = np.arange(-hw, hw + 1) * dz
            kernel = np.exp(-0.5 * (kernel_x / sigma_gauss_conv) ** 2)
            kernel /= kernel.sum()
            nz_conv = np.convolve(nz_bin_norm, kernel, mode='same')
            # renormalize after convolution to preserve unit area within the bin
            area_conv = np.trapezoid(nz_conv, z)
            if area_conv > 0:
                nz_conv = nz_conv / area_conv

            # store this bin's smoothed distribution
            binned_nz_list.append(nz_conv)


        # Save z and per-bin n(z) to a text file: first column z, then columns for each bin
        data = np.column_stack([z] + binned_nz_list)
        #header = "z " + " ".join([f"bin{i+1}" for i in range(num_bins)])
        out_fname = f"lsst_y10_{sample}.nz"
        np.savetxt(out_fname, data, fmt="%.18e")
        print(f"Saved binned distributions to {out_fname}")