"""
import params into single variable
Note that most params will be saved in the URI_PARAMS_RUN1 spreadsheet.
"""

import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#%%
path_params = r'C:\Users\YLuo\VSCode\URI_Calculator_v1_1_TEMPLATE_v4\URI_Calculator_v1_1_TEMPLATE\5_PARAMS\URI_PARAMS_v_1_1.xlsx'
data_directory = r'path to data directory'

#%% create params variable

PATHNAMES = pd.read_excel(path_params, sheet_name='PATHNAMES', index_col=0)
PARAMS = pd.read_excel(path_params, sheet_name='PARAMS', index_col=0)
SETTINGS = pd.read_excel(path_params, sheet_name='SETTINGS', index_col=0)
HARDCODED = pd.read_excel(path_params, sheet_name='HARDCODED', index_col=0)
ABBREVIATIONS = pd.read_excel(path_params, sheet_name='ABBREVIATIONS', header=None)
MITIGATION = pd.read_excel(path_params, sheet_name='RESILIENCE', skiprows=1)
CONSEQUENCES = pd.read_excel(path_params, sheet_name='CONSEQUENCES', skiprows=1)

#%% create names

