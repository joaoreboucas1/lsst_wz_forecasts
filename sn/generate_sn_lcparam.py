# DHFS - MUST run from ./lsst_wz_forecasts

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import camb
import os
import argparse

home = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument("--year",type=int,default=1,help='The LSST SN Year. Available options: `1` or `10`.')
parser.add_argument("--sys_id",type=int,default=0,help='The systematic covariance index. Available options: `0`,...,`7`.')
args = parser.parse_args()

if args.year not in [1,10]:
    raise ValueError('LSST Year: Available options are `y1`, `y10`.')

if args.sys_id not in list(range(7)):
    raise ValueError('Systematic covariance index: Available options are `0`,...,`7`.')

print(f'Using LSST year = {args.year}')
print(f'Using systematic covariance index = {args.sys_id}')

if args.year == 1: 
    obs = 'DDF' # observational strategy
elif args.year == 10:
    obs = 'DDF_WFD'

# Get the redshift and the statistical errors for ...
lcp_old = f'lcparam_Y{args.year}_{obs}_FOUNDATION.txt'
zcmb = np.loadtxt(f'sn/sn_lsst_data/Y{args.year}_{obs}_FOUNDATION/{lcp_old}')[:,1]
dmb  = np.loadtxt(f'sn/sn_lsst_data/Y{args.year}_{obs}_FOUNDATION/{lcp_old}')[:,5]

######################################
## WRITE LCPARAM IN COBAYA-LIKE FORMAT
######################################
# DHFS Note: 
# same cosmological parameters used to generate
# the 3x2pt covariance matrix w/ CosmoCov
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

lcp_new = f'lcparam_Y{args.year}_{obs}_FOUNDATION_CosmoCovFidParams.txt'
path_lcp = f'sn/sn_lsst_data/Y{args.year}_{obs}_FOUNDATION/{lcp_new}'

with open(path_lcp,'w') as f_lcp:
    f_lcp.write(header)
    for i in range(len(zcmb)):
        f_lcp.write(f'name{i} {zcmb[i]} {zcmb[i]} {0.0} {mB[i]:.6f} {dmb[i]}'+f' {0}'*12+'\n') 

####################################
## WRITE COFIG IN COBAYA-LIKE FORMAT
####################################
template = f"""name = JLA
data_file = {lcp_new}
pecz = 0
intrinsicdisp = 0
twoscriptmfit = F
scriptmcut = 10.0
has_mag_covmat = T
mag_covmat_file = sys_Y{args.year}_{obs}_FOUNDATION_{args.sys_id}.txt
has_stretch_covmat = F
has_colour_covmat = F
has_mag_stretch_covmat = F
has_mag_colour_covmat = F
has_stretch_colour_covmat = F"""

dataset=f'sn/sn_lsst_data/Y{args.year}_{obs}_FOUNDATION/Y{args.year}_{obs}_FOUNDATION_{args.sys_id}_CosmoCovFidParams.dataset'

with open(f'{dataset}','w') as f_conf:
    f_conf.write(template) 