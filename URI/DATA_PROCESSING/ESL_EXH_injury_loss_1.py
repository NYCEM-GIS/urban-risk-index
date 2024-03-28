""" deaths due to winter storms"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% load hospitalizations.  These are the most severe injuries
path_hosp = params.PATHNAMES.at['ESL_EXH_hosp_data', 'Value']
df_hosp = pd.read_csv(path_hosp, skiprows=14, skipfooter=5, engine='python')
#keey only the borough estimates
df_hosp = df_hosp.loc[df_hosp['Geography Name'] != 'New York City', :]

#%% add borough code to hosp data
path_borid = params.PATHNAMES.at['Borough_to_FIP', 'Value']
df_borid = pd.read_excel(path_borid)
df_hosp['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_hosp['Geography Name']]

#%% get borough specific average
df_bor = df_hosp[['Bor_ID', 'Y Value']].groupby('Bor_ID').mean()

#%% open 2016 data to convert from age-adjusted to annual rate
path_2016 = params.PATHNAMES.at['ESL_EXH_hosp_2016', 'Value']
df_2016 = pd.read_csv(path_2016, skiprows=6, skipfooter=23, engine='python')
df_2016['ratio'] = df_2016['Estimated Annual Rate (per 100,000 residents)'] /  df_2016['Age-Adjusted Rate (per 100,000 residents)']
df_2016['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_2016['Borough']]
df_bor['Hosp_per_100000'] = [df_bor.at[x, 'Y Value'] * df_2016.loc[df_2016.Bor_ID==x, 'ratio'].values[0] for x in df_bor.index]

#%% calculate tract hospitalization rate
def calc_tract_hosp(BCT_txt):
    idx = gdf_tract.index[gdf_tract.BCT_txt==BCT_txt][0]
    this_bor = gdf_tract.at[idx, 'borocode']
    this_pop = gdf_tract.at[idx, 'pop_2020']
    this_hosp_rate = df_bor.at[int(this_bor), 'Hosp_per_100000']
    return this_pop * this_hosp_rate / 100000.
gdf_tract['N_hosp'] = gdf_tract.apply(lambda x: calc_tract_hosp(x['BCT_txt']), axis=1)

#%% calculate number of emergeny room visits
path_emerg = params.PATHNAMES.at['ESL_EXH_emerg_data', 'Value']
df_emerg = pd.read_csv(path_emerg, skiprows=14, skipfooter=5, engine='python')
#keey only the borough estimates
df_emerg = df_emerg.loc[df_emerg['Geography Name'] != 'New York City', :]

#%% add borough code to emerg data
df_emerg['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_emerg['Geography Name']]

#%% get borough specific average
df_bor = df_emerg[['Bor_ID', 'Y Value']].groupby('Bor_ID').mean()

#%% open 2016 data to convert from age-adjusted to annual rate
path_2016 = params.PATHNAMES.at['ESL_EXH_emerg_2016', 'Value']
df_2016 = pd.read_csv(path_2016, skiprows=6, skipfooter=23, engine='python')
df_2016['ratio'] = df_2016['Estimated Annual Rate (per 100,000 residents)'] /  df_2016['Age-Adjusted Rate (per 100,000 residents)']
df_2016['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_2016['Borough']]
df_bor['Emerg_per_100000'] = [df_bor.at[x, 'Y Value'] * df_2016.loc[df_2016.Bor_ID==x, 'ratio'].values[0] for x in df_bor.index]

#%% calculate tract hospitalization rate
def calc_tract_emerg(BCT_txt):
    idx = gdf_tract.index[gdf_tract.BCT_txt==BCT_txt][0]
    this_bor = gdf_tract.at[idx, 'borocode']
    this_pop = gdf_tract.at[idx, 'pop_2020']
    this_hosp_rate = df_bor.at[int(this_bor), 'Emerg_per_100000']
    return this_pop * this_hosp_rate / 100000.
gdf_tract['N_emerg'] = gdf_tract.apply(lambda x: calc_tract_emerg(x['BCT_txt']), axis=1)

#%% assume all hospital visits start as emergeny room visits
#so the unique emergency room visits will be N_emerg - N_hosp
gdf_tract['N_emerg_uniq'] = gdf_tract['N_emerg'] - gdf_tract['N_hosp']

#%% convert to loss.   Asssume emergency room visits with no hospitalization are "moderate" injuries.
#Assume hospitalizations are "serious" injuries
loss_per_moderate_injury_2016 = params.PARAMS.at['value_moderate_injury', 'Value']
loss_moderate_total = utils.convert_USD(loss_per_moderate_injury_2016, 2016)
loss_per_serious_injury_2016 = params.PARAMS.at['value_serious_injury', 'Value']
loss_serious_total = utils.convert_USD(loss_per_serious_injury_2016, 2016)
gdf_tract['Loss_USD'] = gdf_tract['N_hosp'] * loss_serious_total + gdf_tract['N_emerg_uniq'] * loss_moderate_total

#%% save as output
path_output = params.PATHNAMES.at['ESL_EXT_loss_injury', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='EXH: Injuries Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_output)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating EXH injury loss.")