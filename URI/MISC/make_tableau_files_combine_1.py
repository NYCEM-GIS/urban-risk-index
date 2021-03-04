""" combine 4 tableau csvs (different geographies) into 1 """


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
folder_csvs = r'C:\temp\\'

#%%load Boro
path_boro = os.path.join(folder_csvs, 'TBL_'+'BORO' + '_v1.csv')
df_boro = pd.read_csv(path_boro)
df_all =df_boro.copy()
df_all.rename(columns={"Boro_Code":"GeoID"}, inplace=True)

#%% load citywide
path_citywide = os.path.join(folder_csvs, 'TBL_'+'CITYWIDE' + '_v1.csv')
df_citywide = pd.read_csv(path_citywide)
df_citywide.rename(columns={"Citywide":"GeoID"}, inplace=True)
df_all = df_all.append(df_citywide)

#%% load PUMA
path_puma = os.path.join(folder_csvs, 'TBL_'+'PUMA' + '_v1.csv')
df_PUMA = pd.read_csv(path_puma)
df_PUMA.rename(columns={"PUMA":"GeoID"}, inplace=True)
df_all = df_all.append(df_PUMA)

#%% load NTA
path_NTA = os.path.join(folder_csvs, 'TBL_'+'NTA' + '_v1.csv')
df_NTA = pd.read_csv(path_NTA)
df_NTA.rename(columns={"NTA_Name":"GeoID"}, inplace=True)
df_all = df_all.append(df_NTA)

#%% load tract
path_tracts = os.path.join(folder_csvs, 'TBL_'+'Tracts' + '_v1.csv')
df_tracts = pd.read_csv(path_tracts)
df_tracts.rename(columns={"Census_Tract":"GeoID"}, inplace=True)
df_all = df_all.append(df_tracts)



#%% clean up and add index
df_all.rename(columns={'Unnamed: 0':'RowID'}, inplace=True)
df_all['RowID'] = np.arange(len(df_all))

#%% check quality
if len(df_all) == len(df_boro) + len(df_PUMA) + len(df_NTA) + len(df_tracts) + len(df_citywide):
    print("Field number check: passed.")
else:
    print("Field number check: failed.")

#%% save file
df_all.to_csv(r'C:\temp\\TBL_Master.csv')



