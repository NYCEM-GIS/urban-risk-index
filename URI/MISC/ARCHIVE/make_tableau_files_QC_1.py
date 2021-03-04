""" QC files"""

""" make tableau files"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats
from osgeo import ogr
from shapely.wkt import loads

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load csvs
df_B = pd.read_csv(r'C:\temp\TBL_BORO_v1.csv')
df_P = pd.read_csv(r'C:\temp\TBL_PUMA_v1.csv')
df_N = pd.read_csv(r'C:\temp\TBL_NTA_v1.csv')
df_T = pd.read_csv(r'C:\temp\TBL_Tracts_v1.csv')

#%% check the total expected loss is the same
list_df = [df_B, df_P, df_N]

for df in list_df:
    x = df.loc[ (df.Hazard == 'All') & (df.Component == 'Expected Loss') & \
                            (df["Sub-Component"] == 'All') &  (df.Factor == 'All') & (df.View == 'Raw Value') & \
                            (df.Normalization == 'None'), 'Value'].sum()
    print(x)