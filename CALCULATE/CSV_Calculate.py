""" produce CSV tables
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()
nan_value = 'NA'


#%% loop through geographies
list_geo = ['CITYWIDE', 'BOROCODE', 'PUMA', 'NTA', ]
list_geo_folder = ['CITYWIDE', 'Borough', 'PUMA', 'NTA']
list_geo_keep = []
#for (geo_id, geo_name) in zip(list_geo, list_geo_folder):

geo_id = 'BOROCODE'
geo_name = 'Borough'
list_geo_keep.append(geo_id)
#%% create empty dataframe
list_col_csv = ['RowID', 'GeoID', 'Value', 'Land_Area', 'Pop_2010', 'Bldc_Count',
                'Bldg_Area', 'Geography', 'Hazard', 'Component', 'Sub-Component',
                'Factor', 'View', 'Type', 'Normalization', 'NTA_Name', 'PUMA',
                'Boro_Code', 'Boro_Name']
df_csv = pd.DataFrame(columns = list_col_csv)

#%% loop through each uri hazard
haz = 'EXH'
path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
gdf_haz = gpd.read_file(path_haz)

#%% loop through each column and add based on title
list_col_add = [col for col in gdf_haz.columns if haz in col[0:3]]
this_col = list_col_add[0]

#%% add base to df_temp
list_norm_keep = ['AREA_SQMI', 'FLOOR_SQFT', 'POP']
list_col_keep = list_geo_keep + list_norm_keep + col
this_df_haz = gdf_haz[[col]]

#%%
path_norm = params.PATHNAMES.at['OTH_normalize_values', 'Value']
df_norm = gpd.read_file(path_norm)


