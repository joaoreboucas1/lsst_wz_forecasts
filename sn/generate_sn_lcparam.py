# DHFS - MUST run from ./lsst_wz_forecasts

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import camb
import os

home = os.getcwd()

##############
## Input files
##############
snp     = 'sn/sn_lsst_data'
y1      = 'Y1_DDF_FOUNDATION'
y10     = 'Y10_DDF_WFD_FOUNDATION'
lcp_y1  = 'lcparam_Y1_DDF_FOUNDATION.txt'
lcp_y10 = 'lcparam_Y10_DDF_WFD_FOUNDATION.txt'

zcmb_y1 = np.loadtxt(f'{snp}/{y1}/{lcp_y1}')[:,1]
dmb_y1 = np.loadtxt(f'{snp}/{y1}/{lcp_y1}')[:,5]

zcmb_y10 = np.loadtxt(f'{snp}/{y10}/{lcp_y10}')[:,1]
dmb_y10 = np.loadtxt(f'{snp}/{y10}/{lcp_y10}')[:,5]

zcmb = zcmb_y1 

######################################
## WRITE LCPARAM IN COBAYA-LIKE FORMAT
######################################
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

## Start CAMB to get the apparent magnitude in B-band (mB) assuming LCDM
c_kms = camb.constants.c * 1e-3 # speed of light in km/s
pc = 1e-6 # 1pc = 10^-6 Mpc

results = camb.get_background(cosmo)
MB = -19.0
A5 = 5.0 * np.log10(c_kms/(cosmo.H0*10.0*pc)) ## ~ 43 - see Eq A5 in Union3 2311.12098

dL = results.luminosity_distance(zcmb)
# mB = MB + A5 + 5 * np.log10(dL) ## ~ 25 + 5log(dL) - see Eq A6 in Union3 or Eq 4 in DESY5-SN 2401.02929
mB = 25 + 5 * np.log10(dL) ## 25 + 5log(dL) Return a best model with data from sn_data/DESY5/DES-SN5YR_HD.csv

header = '#name zcmb zhel dz mb dmb x1 dx1 color dcolor 3rdvar d3rdvar cov_m_s cov_m_c cov_s_c set ra dec biascor\n'

path_lcp = f'{home}/{snp}/{y1}/lcparam_lsst_y1.txt'
with open(path_lcp,'w') as f_lcp:
    f_lcp.write(header)
    for i in range(len(zcmb)):
        f_lcp.write(f'name{i} {zcmb[i]} {zcmb[i]} {0.0} {mB[i]:.6f} {dmb_y1[i]}'+f' {0}'*12+'\n') 

############################################
## WRITE COFIG IN COBAYA-LIKE FORMAT
############################################
# full_long_1 = 'pecz = 0\nintrinsicdisp = 0\ntwoscriptmfit = F\nscriptmcut = 10.0\nhas_mag_covmat = T\n' # taken from sn_data/Union3/full_long.dataset 
# full_long_2 = 'has_stretch_covmat = F\nhas_colour_covmat = F\nhas_mag_stretch_covmat = F\nhas_mag_colour_covmat = F\nhas_stretch_colour_covmat = F\n' # taken from sn_data/Union3/full_long.dataset 
# header_TEMPLATE = '#name zcmb zhel dz mb dmb x1 dx1 color dcolor 3rdvar d3rdvar cov_m_s cov_m_c cov_s_c set ra dec biascor\n' # taken from sn_data/Union3/full_long.dataset 

# with open(f'{home}/sn_roman_sims/ROMAN_SIM_{idx}/config_ROMAN_SIM_{idx}.dataset','w') as f_conf:
#     f_conf.write(f'name = ROMAN_SIM_{idx}\n') # see sn_data/DESY5/config.dataset
#     f_conf.write(full_long_1)
#     f_conf.write(f'data_file = ROMAN_SIM_{idx}/lcparam_ROMAN_SIM_{idx}.txt\n')
#     f_conf.write(full_long_2)
#     f_conf.write(f'mag_covmat_file = ROMAN_SIM_{idx}/covmat_ROMAN_SIM_{idx}.txt\n')

# print("idx:",idx)