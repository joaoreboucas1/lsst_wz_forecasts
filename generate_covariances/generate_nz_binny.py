import cmasher as cmr
import matplotlib.pyplot as plt
import numpy as np

from binny import NZTomography

def plot_bins(result):
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(11.5, 8.0),
    )

    panel_order = [
        (("lens", "1"), "Lens bins Y1"),
        (("source", "1"), "Source bins Y1"),
        (("lens", "10"), "Lens bins Y10"),
        (("source", "10"), "Source bins Y10"),
    ]



    for ax, ((role, year), title) in zip(axes.ravel(), panel_order, strict=True):
        z = result[(role, year)].z
        bin_dict = result[(role, year)].bins
        bin_indices = sorted(bin_dict.keys())
        colors = cmr.take_cmap_colors(
            "viridis",
            len(bin_indices),
            cmap_range=(0.1, 0.9),
            return_fmt="hex",
        )
        for i, (color, bin_index) in enumerate(zip(colors, bin_indices, strict=True)):
            curve = np.asarray(bin_dict[bin_index], dtype=float)

            ax.fill_between(
                z,
                0.0,
                curve,
                color=color,
                alpha=0.65,
                linewidth=0.0,
                zorder=10 + i,
            )

            ax.plot(
                z,
                curve,
                color="k",
                linewidth=1.8,
                zorder=20 + i,
            )

        ax.plot(z, np.zeros_like(z), color="k", linewidth=2.0, zorder=1000)

        ax.set_title(title)
        ax.set_xlabel("Redshift $z$")
        if role == "lens":
            ax.set_xlim(0.0, 1.5)

    axes[0, 0].set_ylabel(r"Normalized $n_i(z)$")
    axes[1, 0].set_ylabel(r"Normalized $n_i(z)$")

    plt.suptitle("LSST survey preset tomography", fontsize=16)

    plt.tight_layout(rect=(0, 0, 1, 0.97))
    plt.show()

def save_bins(result):

    cases = [
        ("lens", "1"),
        ("source", "1"),
        ("lens", "10"),
        ("source", "10"),
    ]


    for role, year in cases:
        z = result[(role, year)].z
        bin_dict = result[(role, year)].bins
        bin_indices = sorted(bin_dict.keys())
        data = np.vstack([z] + [np.asarray(bin_dict[i]) for i in bin_indices]).T
        np.savetxt(f"lsst_y{year}_{role}_binny.nz", data)


results = {}

for role in ["lens", "source"]:
    for year in ["1", "10"]:
        tomo = NZTomography()
        results[(role, year)] = tomo.build_survey_bins(
            "lsst",
            role=role,
            year=year,
            include_tomo_metadata=True,
        )

# plot_bins(results)
save_bins(results)
