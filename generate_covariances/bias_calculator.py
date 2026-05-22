import numpy as np
import camb
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

np.set_printoptions(legacy='1.25')

omegam = 0.319
omegab = 0.049
h      = 0.67
omegach2 = (omegam - omegab)*h*h - 0.06/93.15
As     = 2.1e-9
ns     = 0.96
w0     = -1
wa     = -0

cosmo = camb.set_params(
    ombh2=omegab*h*h,
    omch2=omegach2,
    H0=100*h,
    As=As,
    ns=ns,
    WantTransfer=True
)

z_growth = np.linspace(0, 3, 500)
cosmo.TransferRedshiftList = list(z_growth)
cosmo.TransferNumRedshifts = len(z_growth)

results = camb.get_results(cosmo)
sigma8 = results.get_sigma8_0()
print(f"{sigma8 = }")

D_z = results.get_redshift_evolution([1e-5], z_growth, ['delta_tot'])[0,:,0]
D_z /= D_z[0]

# Y1 n(z)
y1_lens_nz_data = np.loadtxt("lsst_y1_lens.nz", unpack=True)
z, n1, n2, n3, n4, n5 = y1_lens_nz_data
lens_mean_redshifts = []
for bin_nz in [n1, n2, n3, n4, n5]:
    mean = np.sum(z*bin_nz)/np.sum(bin_nz)
    lens_mean_redshifts.append(mean)

D_z_interp = interp1d(z_growth, D_z)
print("Fiducial bias for Y1")
for z in lens_mean_redshifts:
    b = 1.05/D_z_interp(z)
    print(f"{z = } => {b = }")
