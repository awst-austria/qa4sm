from django.conf import settings
from datetime import datetime


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
ISMN_V20210131 = 'ISMN_V20210131'
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

NOT_AS_REFERENCE = [SMAP, SMOS, ASCAT]

IRREGULAR_GRIDS = {'SMAP' : 0.35,
                   'SMOS' : 0.25,
                   'ASCAT' : 0.1}

START_TIME = datetime(1978, 1, 1).strftime('%Y-%m-%d')
END_TIME = datetime.now().strftime('%Y-%m-%d')

