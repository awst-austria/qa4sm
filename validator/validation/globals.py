from django.conf import settings
from datetime import datetime
import pandas as pd
import numpy as np
from validator.models import ValidationRun

OUTPUT_FOLDER = settings.MEDIA_ROOT

METRICS = {'R': 'Pearson\'s r',
           'p_R': 'Pearson\'s r p-value',
           'rho': 'Spearman\'s rho',
           'p_rho': 'Spearman\'s rho p-value',
           'RMSD': 'Root-mean-square deviation',
           'BIAS': 'Bias (difference of means)',
           'n_obs': '# observations',
           'status': '# status',
           'urmsd': 'Unbiased root-mean-square deviation',
           'RSS': 'Residual sum of squares',
           'mse': 'Mean square error',
           'mse_corr': 'Mean square error correlation',
           'mse_bias': 'Mean square error bias',
           'mse_var': 'Mean square error variance', }

METRIC_TEMPLATE = ["overview_{id_ref}-{ds_ref}_and_{id_sat}-{ds_sat}_",
                   "{metric}"]

TC_METRICS = {'snr': 'TC: Signal-to-noise ratio',
              'err_std': 'TC: Error standard deviation',
              'beta': 'TC: Scaling coefficient', }

TC_METRIC_TEMPLATE = ["overview_{id_ref}-{ds_ref}_and_{id_sat}-{ds_sat}_and_{id_sat2}-{ds_sat2}",
                      "_{metric}",
                      "_for_{id_met}-{ds_met}"]

C3SC = 'C3S_combined'
ISMN = 'ISMN'
GLDAS = 'GLDAS'
SMAP_L3 = 'SMAP_L3'
ASCAT = 'ASCAT'
CCIC = 'ESA_CCI_SM_combined'
CCIA = 'ESA_CCI_SM_active'
CCIP = 'ESA_CCI_SM_passive'
SMOS_IC = 'SMOS_IC'
ERA5 = 'ERA5'
ERA5_LAND = 'ERA5_LAND'
CGLS_CSAR_SSM1km = 'CGLS_CSAR_SSM1km'
CGLS_SCATSAR_SWI1km = 'CGLS_SCATSAR_SWI1km'
SMOS_L3 = 'SMOS_L3'
SMOS_L2 = 'SMOS_L2'
SMAP_L2 = 'SMAP_L2'
SMOS_SBPCA = 'SMOS_SBPCA'

# dataset versions
C3S_V201706 = 'C3S_V201706'
C3S_V201812 = 'C3S_V201812'
C3S_V201912 = 'C3S_V201912'
C3S_V202012 = 'C3S_V202012'
C3S_V202212 = 'C3S_V202212'
ISMN_V20180712_MINI = 'ISMN_V20180712_MINI'
ISMN_V20191211 = 'ISMN_V20191211'
ISMN_V20210131 = 'ISMN_V20210131'
ISMN_VRelease2_Verification = 'ISMN_VRelease2_Verification'
ISMN_V20230110 = 'ISMN_V20230110'
SMAP_V5_PM = 'SMAP_V5_PM'
SMAP_V6_PM = 'SMAP_V6_PM'
SMAP_V5_AM = 'SMAP_V5_AM'
SMAP_V6_AM = 'SMAP_V6_AM'
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
ESA_CCI_SM_A_V06_1 = 'ESA_CCI_SM_A_V06_1'
ESA_CCI_SM_P_V06_1 = 'ESA_CCI_SM_P_V06_1'
ESA_CCI_SM_C_V06_1 = 'ESA_CCI_SM_C_V06_1'
ESA_CCI_SM_A_V07_1 = 'ESA_CCI_SM_A_V07_1'
ESA_CCI_SM_P_V07_1 = 'ESA_CCI_SM_P_V07_1'
ESA_CCI_SM_C_V07_1 = 'ESA_CCI_SM_C_V07_1'
ESA_CCI_SM_A_V08_1 = 'ESA_CCI_SM_A_V08_1'
ESA_CCI_SM_P_V08_1 = 'ESA_CCI_SM_P_V08_1'
ESA_CCI_SM_C_V08_1 = 'ESA_CCI_SM_C_V08_1'
CGLS_CSAR_SSM1km_V1_1 = 'CGLS_CSAR_SSM1km_V1_1'
CGLS_SCATSAR_SWI1km_V1_0 = 'CGLS_SCATSAR_SWI1km_V1_0'
SMOSL3_Level3_DESC = 'SMOSL3_v339_DESC'
SMOSL3_Level3_ASC = 'SMOSL3_v339_ASC'
SMOSL2_700 = 'SMOSL2_v700'
SMAPL2_V8 = 'SMAPL2_V8'
SMOS_SBPCA_v724 = 'SMOS_SBPCA_v724'

# dataset data variables PRETTY NAMES
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
SMOSL3_sm = 'SMOSL3_sm'
SMOSL2_sm = 'SMOSL2_sm'
SMAPL2_soil_moisture = 'SMAPL2_soil_moisture'
SMOS_SBPCA_sm = 'SMOS_SBPCA_sm'

# left empty, because if in the future we want to exclude some datasets from the reference group it will be enough to
# insert it's shortname to the list
NOT_AS_REFERENCE = []

# ValidationRun and Datasets fields for comparison when looking for a validation with the same settings
VR_FIELDS = ['interval_from', 'interval_to', 'max_lat', 'min_lat', 'max_lon', 'min_lon', 'tcol',
             'bootstrap_tcol_cis', 'anomalies', 'anomalies_from', 'anomalies_to', 'temporal_matching']
DS_FIELDS = ['dataset', 'version', 'is_spatial_reference', 'is_temporal_reference']

IRREGULAR_GRIDS = {'SMAP_L3': 0.35,
                   'SMOS_L3': 0.25,
                   'SMOS_IC': 0.25,
                   'ASCAT': 0.1,
                   'SMOS_L2': 0.135,  # 15km
                   'SMOS_SBPCA': 0.135,  # 15km
                   'SMAP_L2': 0.35, }  # 35km

START_TIME = datetime(1978, 1, 1).strftime('%Y-%m-%d')
END_TIME = datetime.now().strftime('%Y-%m-%d')

METADATA_TEMPLATE = {'other_ref': None,
                     'ismn_ref': {'clay_fraction': np.float32([np.nan]),
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
                                  'timerange_from': np.array([' ' * 256]),
                                  'timerange_to': np.array([' ' * 256]),
                                  'variable': np.array([' ' * 256]),
                                  'instrument_depthfrom': np.float32([np.nan]),
                                  'instrument_depthto': np.float32([np.nan]),
                                  # only available for FRM4SM ISMN version(s)
                                  'frm_class': np.array([' ' * 256]),
                                  }
                     }

INSTRUMENT_META = "instrument"
MEASURE_DEPTH_FROM = "instrument_depthfrom"
MEASURE_DEPTH_TO = "instrument_depthto"
METADATA_PLOT_NAMES = {"Land cover classification": "metadata_lc_2010",
                       "Climate classification": "metadata_climate_KG",
                       "Soil type classification": "metadata_instrument_depth_and_soil_type",
                       "FRM classification": "metadata_frm_class",
                       }

TEMP_MATCH_WINDOW = ValidationRun.TEMP_MATCH_WINDOW

# scaling methods
SCALING_METHODS = ValidationRun.SCALING_METHODS

USER_DATASET_MIN_ID = 200
USER_DATASET_VERSION_MIN_ID = 500
USER_DATASET_VARIABLE_MIN_ID = 500

ISMN_LIST_FILE_NAME = 'ismn_station_list.csv'
GEOJSON_FILE_NAME = 'ismn_sensors.json'


