from django.conf import settings
from datetime import datetime
import pandas as pd
import numpy as np


OUTPUT_FOLDER = settings.MEDIA_ROOT

METRICS = {'R' : 'Pearson\'s r',
           'p_R' : 'Pearson\'s r p-value',
           'rho' : 'Spearman\'s rho',
           'p_rho' : 'Spearman\'s rho p-value',
           'RMSD' : 'Root-mean-square deviation',
           'BIAS' : 'Bias (difference of means)',
           'n_obs' : '# observations',
           'urmsd' : 'Unbiased root-mean-square deviation',
           'RSS' : 'Residual sum of squares',
           'mse' : 'Mean square error',
           'mse_corr' : 'Mean square error correlation',
           'mse_bias' : 'Mean square error bias',
           'mse_var' : 'Mean square error variance',}

METRIC_TEMPLATE = ["overview_{id_ref}-{ds_ref}_and_{id_sat}-{ds_sat}_",
                   "{metric}"]

TC_METRICS = {'snr': 'TC: Signal-to-noise ratio',
              'err_std': 'TC: Error standard deviation',
              'beta': 'TC: Scaling coefficient',}

TC_METRIC_TEMPLATE = ["overview_{id_ref}-{ds_ref}_and_{id_sat}-{ds_sat}_and_{id_sat2}-{ds_sat2}",
                      "_{metric}",
                      "_for_{id_met}-{ds_met}"]

C3S = 'C3S'
ISMN = 'ISMN'
GLDAS = 'GLDAS'
SMAP = 'SMAP'
ASCAT = 'ASCAT'
CCI = 'ESA_CCI_SM_combined'
CCIA = 'ESA_CCI_SM_active'
CCIP = 'ESA_CCI_SM_passive'
SMOS = 'SMOS'
ERA5 = 'ERA5'
ERA5_LAND = 'ERA5_LAND'

## dataset versions
C3S_V201706 = 'C3S_V201706'
C3S_V201812 = 'C3S_V201812'
C3S_V201912 = 'C3S_V201912'
ISMN_V20180712_MINI = 'ISMN_V20180712_MINI'
ISMN_V20191211 = 'ISMN_V20191211'
SMAP_V5_PM = 'SMAP_V5_PM'
SMAP_V6_PM = 'SMAP_V6_PM'
SMOS_105_ASC = 'SMOS_105_ASC'
GLDAS_NOAH025_3H_2_1 = 'GLDAS_NOAH025_3H_2_1'
ASCAT_H113 = 'ASCAT_H113'
ERA5_20190613 = 'ERA5_20190613'
ERA5_Land_V20190904 = 'ERA5_LAND_V20190904'
ESA_CCI_SM_A_V04_4 = 'ESA_CCI_SM_A_V04_4'
ESA_CCI_SM_P_V04_4 = 'ESA_CCI_SM_P_V04_4'
ESA_CCI_SM_C_V04_4 = 'ESA_CCI_SM_C_V04_4'
ESA_CCI_SM_A_V04_5 = 'ESA_CCI_SM_A_V04_5'
ESA_CCI_SM_P_V04_5 = 'ESA_CCI_SM_P_V04_5'
ESA_CCI_SM_C_V04_5 = 'ESA_CCI_SM_C_V04_5'
ESA_CCI_SM_C_V04_7 = 'ESA_CCI_SM_C_V04_7'
ESA_CCI_SM_A_V05_2 = 'ESA_CCI_SM_A_V05_2'
ESA_CCI_SM_P_V05_2 = 'ESA_CCI_SM_P_V05_2'
ESA_CCI_SM_C_V05_2 = 'ESA_CCI_SM_C_V05_2'

## dataset data variables
C3S_sm = 'C3S_sm'
SMAP_soil_moisture = 'SMAP_soil_moisture'
SMOS_sm = 'SMOS_sm'
ASCAT_sm = 'ASCAT_sm'
ISMN_soil_moisture = 'ISMN_soil_moisture'
GLDAS_SoilMoi0_10cm_inst = 'GLDAS_SoilMoi0_10cm_inst'
GLDAS_SoilMoi10_40cm_inst = 'GLDAS_SoilMoi10_40cm_inst'
GLDAS_SoilMoi40_100cm_inst = 'GLDAS_SoilMoi40_100cm_inst'
GLDAS_SoilMoi100_200cm_inst = 'GLDAS_SoilMoi100_200cm_inst'
ERA5_sm = 'ERA5_sm'
ERA5_LAND_sm = 'ERA5_LAND_sm'
ESA_CCI_SM_P_sm = 'ESA_CCI_SM_P_sm'
ESA_CCI_SM_A_sm = 'ESA_CCI_SM_A_sm'
ESA_CCI_SM_C_sm = 'ESA_CCI_SM_C_sm'


# left empty, because if in the future we want to exclude some datasets from the reference group it will be enough to
# insert it's shortname to the list
NOT_AS_REFERENCE = []


# ValidationRun and Datasets fields for comparison when looking for a validation with the same settings
VR_FIELDS = ['interval_from', 'interval_to', 'max_lat', 'min_lat', 'max_lon', 'min_lon', 'tcol',
                 'anomalies', 'anomalies_from', 'anomalies_to']
DS_FIELDS = ['dataset', 'version']

IRREGULAR_GRIDS = {'SMAP' : 0.35,
                   'SMOS' : 0.25,
                   'ASCAT' : 0.1}

START_TIME = datetime(1978, 1, 1).strftime('%Y-%m-%d')
END_TIME = datetime.now().strftime('%Y-%m-%d')

METADATA_TEMPLATE = {'clay_fraction': np.float32([np.nan]),
                     'climate_KG': np.array([' ' * 256]),
                     'climate_insitu': np.array([' ' * 256]),
                     'elevation': np.float32([np.nan]),
                     'instrument': np.array([' ' * 256]),
                     'latitude': np.float32([np.nan]),
                     'lc_2000': np.float32([np.nan]),
                     'lc_2005': np.float32([np.nan]),
                     'lc_2010': np.float32([np.nan]),
                     'lc_insitu': np.array([' ' * 256]),
                     'longitude': np.float32([np.nan]),
                     'network': np.array([' ' * 256]),
                     'organic_carbon': np.float32([np.nan]),
                     'sand_fraction': np.float32([np.nan]),
                     'saturation': np.float32([np.nan]),
                     'silt_fraction': np.float32([np.nan]),
                     'station': np.array([' ' * 256]),
                     'timerange_from': np.float32([np.nan]),
                     'timerange_to': np.float32([np.nan]),
                     'variable': np.array([' ' * 256])}
