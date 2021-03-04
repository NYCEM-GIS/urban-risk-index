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
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% load deaths and get average number per year across NYC
path_deaths = params.PATHNAMES.at['ESL_WIW_deaths_data', 'Value']
df_deaths = pd.read_csv(path_deaths, skiprows=9, skipfooter = 5, engine='python')
N_deaths_year_NYC = df_deaths['Y Value'].mean()

#%% load hospitalizations.  assume that deaths are by borough same as the age-adjusted hospitalziation rate
#note it would be better to use unadjusted hospitalization rate, but that is available for only one year
#so may be too noisy
path_hosp = params.PATHNAMES.at['ESL_WIW_hosp_data', 'Value']
df_hosp = pd.read_csv(path_hosp, skiprows=12, skipfooter=5, engine='python')
#remove
df_hosp = df_hosp.loc[df_hosp['Geography Name'] != 'New York City', :]

#%% add borough code to hosp data
path_borid = params.PATHNAMES.at['Borough_to_FIP', 'Value']
df_borid = pd.read_excel(path_borid)
df_hosp['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_hosp['Geography Name']]

#%% get borough specific average
df_bor = df_hosp[['Bor_ID', 'Y Value']].groupby('Bor_ID').mean()

#%% distribute deaths using rate as weight
df_bor['N_deaths_yr'] = N_deaths_year_NYC * df_bor['Y Value'] / df_bor['Y Value'].sum()

#%% distribute deaths by population within each borough
def calc_tract_deaths(BCT_txt):
    idx = gdf_tract.index[gdf_tract.BCT_txt==BCT_txt][0]
    this_bor = gdf_tract.at[idx, 'BOROCODE']
    this_pop = gdf_tract.at[idx, 'pop_2010']
    this_bor_pop = gdf_tract.loc[gdf_tract.BOROCODE==this_bor, 'pop_2010'].sum()
    this_N_deaths = df_bor.at[int(this_bor), 'N_deaths_yr']
    return this_N_deaths * this_pop / this_bor_pop
gdf_tract['N_deaths'] = gdf_tract.apply(lambda x: calc_tract_deaths(x['BCT_txt']), axis=1)


#%% convert to loss
loss_per_death_2016 = params.PARAMS.at['value_of_stat_life_2016', 'Value']
loss_deaths_total = utils.convert_USD(loss_per_death_2016, 2016)
gdf_tract['Loss_USD'] = gdf_tract['N_deaths'] * loss_deaths_total

#%% save as output
path_output = params.PATHNAMES.at['ESL_WIW_loss_deaths', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='WIW: Death Loss',
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
print("Finished calculating WIW death loss.")