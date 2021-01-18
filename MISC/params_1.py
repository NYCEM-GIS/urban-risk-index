"""
import params into single variable
Note that most params will be saved in the URI_PARAMS_RUN1 spreadsheet.
"""

import pandas as pd
import numpy as np

#%%
path_params = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\5_PARAMS\URI_PARAMS_RUN2.xlsx'

#%% create params variable

PATHNAMES = pd.read_excel(path_params, sheet_name='PATHNAMES', index_col=0)
PARAMS = pd.read_excel(path_params, sheet_name='PARAMS', index_col=0)
SETTINGS = pd.read_excel(path_params, sheet_name='SETTINGS', index_col=0)
HARDCODED = pd.read_excel(path_params, sheet_name='HARDCODED', index_col=0)
ABBREVIATIONS = pd.read_excel(path_params, sheet_name='ABBREVIATIONS', header=None)
MITIGATION = pd.read_excel(path_params, sheet_name='MITIGATION', skiprows=1)

#%% create names

