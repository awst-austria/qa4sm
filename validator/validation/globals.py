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

## datasets
ISMN = 'ISMN'
SMOS = 'SMOS'
CGLS_CSAR_SSM1km = 'CGLS_CSAR_SSM1km'

## dataset versions
ISMN_V20191211 = 'ISMN_V20191211'
SMOS_105_ASC = 'SMOS_105_ASC'
CGLS_CSAR_SSM1km_V1_1 = 'CGLS_CSAR_SSM1km_V1_1'

## dataset data variables
ISMN_soil_moisture = 'ISMN_soil_moisture'
SMOS_sm = 'SMOS_sm'
CGLS_CSAR_SSM1km_ssm = 'S1_SSM'


DEFAULT_DATASET = CGLS_CSAR_SSM1km
DEFAULT_REFERENCE = ISMN


NOT_AS_REFERENCE = [CGLS_CSAR_SSM1km, SMOS]

IRREGULAR_GRIDS = {'SMAP' : 0.35,
                   'SMOS' : 0.25,
                   'ASCAT' : 0.1}

START_TIME = datetime(1978, 1, 1).strftime('%Y-%m-%d')
END_TIME = datetime.now().strftime('%Y-%m-%d')
