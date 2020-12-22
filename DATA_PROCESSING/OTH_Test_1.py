""" scratch """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%%

path_URI = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\3_OUTPUTS\URI_FULL\URI_FULL_RES_tract.shp'

gdf_URI = gpd.read_file(path_URI)

#%% merge with tracts
gdf_tract = utils.get_blank_tract()
gdf_URI = gdf_URI.merge(gdf_tract[['BOROCODE', 'NEIGHBORHO', 'PUMA', 'BCT_txt']], on='BCT_txt', how='left')

#%% get population weighted -PUMA
def weight_ave(x, weights):
    if weights.sum()!= 0:
        result =  np.average(x, weights=weights)
    else:
        result = 3
    return result
wm = lambda x: weight_ave(x, weights=gdf_URI.loc[x.index, "pop_2010"])

#%% run for neighborhoods
df_NEIGHBORHO = gdf_URI.groupby(["NEIGHBORHO"]).agg(N_SOV=("SOV", wm),
                                        N_RCA=("RCA", wm),
                                        N_ESL=("ESL", sum)
                                        )
df_NEIGHBORHO['N_URI_Raw'] = df_NEIGHBORHO['N_ESL'] * df_NEIGHBORHO['N_SOV'] / df_NEIGHBORHO['N_RCA']
df_NEIGHBORHO.index.name = 'index'
df_NEIGHBORHO['NEIGHBORHO'] = df_NEIGHBORHO.index
df_NEIGHBORHO = utils.calculate_kmeans(df_NEIGHBORHO, data_column = 'N_URI_Raw', score_column='N_URI',
                                              n_cluster = 5)
gdf_URI = gdf_URI.merge(df_NEIGHBORHO[['N_ESL', 'N_SOV', 'N_RCA', 'N_URI_Raw', 'N_URI', "NEIGHBORHO"]], left_on='NEIGHBORHO', right_on='NEIGHBORHO', how='left')

#%% run for PUMA
df_PUMA = gdf_URI.groupby(["PUMA"]).agg(P_SOV=("SOV", wm),
                                        P_RCA=("RCA", wm),
                                        P_ESL=("ESL", sum)
                                        )
df_PUMA['P_URI_Raw'] = df_PUMA['P_ESL'] * df_PUMA['P_SOV'] / df_PUMA['P_RCA']
df_PUMA.index.name = 'index'
df_PUMA['PUMA'] = df_PUMA.index
df_PUMA = utils.calculate_kmeans(df_PUMA, data_column = 'P_URI_Raw', score_column='P_URI',
                                              n_cluster = 5)
gdf_URI = gdf_URI.merge(df_PUMA[['P_ESL', 'P_SOV', 'P_RCA', 'P_URI_Raw', 'P_URI', 'PUMA']], left_on='PUMA', right_on='PUMA', how='left')

#%% repeat for boros
df_boro = gdf_URI.groupby(["BOROCODE"]).agg(B_SOV=("SOV", wm),
                                        B_RCA=("RCA", wm),
                                        B_ESL=("ESL", sum)
                                        )
df_boro['B_URI_Raw'] = df_boro['B_ESL'] * df_boro['B_SOV'] / df_boro['B_RCA']
df_boro.index.name = 'index'
df_boro['BOROCODE'] = df_boro.index
df_boro = utils.calculate_kmeans(df_boro, data_column = 'B_URI_Raw', score_column='B_URI',
                                              n_cluster = 5)
gdf_URI = gdf_URI.merge(df_boro[['B_ESL', 'B_SOV', 'B_RCA', 'B_URI_Raw', 'B_URI', "BOROCODE"]], left_on='BOROCODE', right_on='BOROCODE', how='left')

#%%
gdf_URI.to_excel(r'C:\temp\test3.xlsx')