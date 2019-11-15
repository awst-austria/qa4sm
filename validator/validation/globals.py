from valentina.settings import MEDIA_ROOT

OUTPUT_FOLDER = MEDIA_ROOT

METRICS = {'R' : 'Pearson\'s r',
           'p_R' : 'Pearson\'s r p-value',
           'rho' : 'Spearman\'s rho',
           'p_rho' : 'Spearman\'s rho p-value',
           'RMSD' : 'Root-mean-square deviation',
           'BIAS' : 'Bias (difference of means)',
           'n_obs' : '# observations',
           'urmsd' : 'Unbiased root-mean-square deviation',
#            'RSS' : 'Residual sum of squares',
           'mse' : 'Mean square error',
           'mse_corr' : 'Mean square error correlation',
           'mse_bias' : 'Mean square error bias',
           'mse_var' : 'Mean square error variance',}

C3S = 'C3S'
ISMN = 'ISMN'
GLDAS = 'GLDAS'
SMAP = 'SMAP'
ASCAT = 'ASCAT'
CCI = 'ESA_CCI_SM_combined'
SMOS = 'SMOS'
ERA5 = 'ERA5'
ERA5_Land = 'ERA5-Land'

## dataset versions
C3S_V201706 = 'C3S_V201706'
ISMN_V20180712_TEST = 'ISMN_V20180712_TEST'
ISMN_V20180712_MINI = 'ISMN_V20180712_MINI'
ISMN_V20180830_GLOBAL = 'ISMN_V20180830_GLOBAL'
SMAP_V5_PM = 'SMAP_V5_PM'
GLDAS_NOAH025_3H_2_1 = 'GLDAS_NOAH025_3H_2_1'
GLDAS_TEST = 'GLDAS_TEST'
ASCAT_H113 = 'ASCAT_H113'
ERA5_test = 'ERA5_test'
ERA5_20190613 = 'ERA5_20190613'
ERA5_Land_V20190904 = 'ERA5-Land_V20190904'
ERA5_Land_test = 'ERA5-Land_test'

## dataset data variables
C3S_sm = 'C3S_sm'
SMAP_soil_moisture = 'SMAP_soil_moisture'
ASCAT_sm = 'ASCAT_sm'
ISMN_soil_moisture = 'ISMN_soil_moisture'
GLDAS_SoilMoi0_10cm_inst = 'GLDAS_SoilMoi0_10cm_inst'
GLDAS_SoilMoi10_40cm_inst = 'GLDAS_SoilMoi10_40cm_inst'
GLDAS_SoilMoi40_100cm_inst = 'GLDAS_SoilMoi40_100cm_inst'
GLDAS_SoilMoi100_200cm_inst = 'GLDAS_SoilMoi100_200cm_inst'
ERA5_sm = 'ERA5_sm'
ERA5_Land_sm = 'ERA5-Land_sm'
