""" open the URI_full andn calculate.  """


#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% get list of hazards
list_hazards = ['EXH', 'WIW', 'CST', 'CER', 'HIW', 'ERQ', 'FLD', 'EMG', 'RES', 'CRN', 'CYB']

#%% get path to full URI shapefiles (produced by the notebooks).  open and create single shapefile with Stfid, haz, and URI_Raw
for i, haz in enumerate(list_hazards):
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
                haz, haz)
    gdf_haz = gpd.read_file(path_haz)
    this_haz = gdf_haz[['BCT_txt', 'URI_Raw', 'N_URI_Raw', 'P_URI_Raw', 'B_URI_Raw']].copy()
    this_haz['haz'] = np.repeat(haz, len(this_haz))
    if i==0:
        df_haz = this_haz.copy()
    else:
        df_haz = df_haz.append(this_haz)

#%% calculate score
df_haz = utils.calculate_kmeans(df_haz, data_column='URI_Raw')
df_haz.rename(columns={'Score':'URI_AllHaz'}, inplace=True)

df_haz = utils.calculate_kmeans(df_haz, data_column='N_URI_Raw')
df_haz.rename(columns={'Score':'N_URI_AllHaz'}, inplace=True)

df_haz = utils.calculate_kmeans(df_haz, data_column='P_URI_Raw')
df_haz.rename(columns={'Score':'P_URI_AllHaz'}, inplace=True)

df_haz = utils.calculate_kmeans(df_haz, data_column='B_URI_Raw')
df_haz.rename(columns={'Score':'B_URI_AllHaz'}, inplace=True)

#%% get path to full URI shapefiles (produced by the notebooks).  open and create single shapefile with Stfid, haz, and URI_Raw
for i, haz in enumerate(list_hazards):
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
                haz, haz)
    gdf_haz = gpd.read_file(path_haz)
    this_haz = df_haz.loc[df_haz['haz']==haz].copy()
    gdf_haz = gdf_haz.merge(this_haz[['BCT_txt', 'URI_AllHaz', 'N_URI_AllHaz', 'P_URI_AllHaz', 'B_URI_AllHaz']], on='BCT_txt', how='inner')
    gdf_haz.to_file(path_haz)


#%%  get URI_Total
# for i, haz in enumerate(list_hazards):
#     path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
#                 haz, haz)
#     gdf_haz = gpd.read_file(path_haz)
#     this_haz = gdf_haz[['BCT_txt', 'URI_Raw']].copy()
#     this_haz['haz'] = np.repeat(haz, len(this_haz))
#     if i==0:
#         df_haz = this_haz.copy()
#     else:
#         df_haz = df_haz.append(this_haz)

