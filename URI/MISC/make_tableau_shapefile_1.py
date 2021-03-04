""" combine tableu shapefiles into 1 shapefile"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%%
path_shp = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\3_OUTPUTS\TABLEAU\\'
list_shapefile = ['Tableau_URI_shapefile.shp', 'Tableau_URI_Neighborhood_shapefile.shp',
                   'Tableau_URI_PUMA_shapefile.shp', 'Tableau_URI_BORO_shapefile.shp',
                   'Tableau_URI_CITYWIDE_shapefile.shp']

#%%load Boro
path_boro = os.path.join(path_shp, list_shapefile[3])
df_boro = gpd.read_file(path_boro)
df_boro['Geography'] = np.repeat('Borough', len(df_boro))
df_all =df_boro.copy()
df_all.rename(columns={"Boro_Code":"GeoID"}, inplace=True)

#%% load PUMA
path_puma = os.path.join(path_shp, list_shapefile[2])
df_PUMA = gpd.read_file(path_puma)
df_PUMA['Geography'] = np.repeat('PUMA', len(df_PUMA))
df_PUMA.rename(columns={"PUMA":"GeoID"}, inplace=True)
df_all = df_all.append(df_PUMA)

#%% load NTA
path_NTA = os.path.join(path_shp, list_shapefile[1])
df_NTA = gpd.read_file(path_NTA)
df_NTA['Geography'] = np.repeat('NTA', len(df_NTA))
df_NTA.rename(columns={"NTA_Name":"GeoID"}, inplace=True)
df_all = df_all.append(df_NTA)

#%% load tract
path_tracts = os.path.join(path_shp, list_shapefile[0])
df_tracts = gpd.read_file(path_tracts)
df_tracts['Geography'] = np.repeat('Tract', len(df_tracts))
df_tracts.rename(columns={"Census_Tra":"GeoID"}, inplace=True)
df_all = df_all.append(df_tracts)

#%% load citywide
path_citywide = os.path.join(path_shp, list_shapefile[4])
df_citywide = gpd.read_file(path_citywide)
df_citywide['Geography'] = np.repeat('Citywide', len(df_citywide))
df_citywide.rename(columns={"Citywide":"GeoID"}, inplace=True)
df_all = df_all.append(df_citywide)

#%% clean up and add index
df_all.rename(columns={'Unnamed: 0':'RowID'}, inplace=True)
df_all['RowID'] = np.arange(len(df_all))
df_all.drop(columns='Index', inplace=True)

#%% check quality
if len(df_all) == len(df_boro) + len(df_PUMA) + len(df_NTA) + len(df_tracts) + len(df_citywide):
    print("Field number check: passed.")
else:
    print("Field number check: failed.")

#%% save file
df_all.to_file(os.path.join(path_shp, 'Tableau_URI_Master_shapefile.shp'))