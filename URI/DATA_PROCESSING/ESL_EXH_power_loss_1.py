""" calculate loss due to power outages
distributed by population
"""

#%% load packages
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_population_tract = PATHNAMES.population_by_tract
# Params
yearly_outage = PARAMS['EXH_outage_person_hrs_per_year'].value
loss_outage_hr = PARAMS['loss_day_power'].value / 24.
# Output paths
path_output = PATHNAMES.ESL_EXH_loss_power

#%% LOAD DATA
df_pop = pd.read_excel(path_population_tract, skiprows=5)

#%%calculate total loss
yearly_loss = yearly_outage * loss_outage_hr

#%%  get tract
gdf_tract = utils.get_blank_tract()

#%% open population and join
df_pop.dropna(inplace=True, subset=['2020 DCP Borough Code', '2020 Census Tract'])
df_pop.rename(columns={2020: 'pop_2020'}, inplace=True)
df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2020 DCP Borough Code'])) + str(int(df_pop.at[x,'2020 Census Tract'])).zfill(6) for x in df_pop.index]
gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2020']], on='BCT_txt', how='left')

#%% distribute cost to each tract by population
pop_total = gdf_tract['pop_2020'].sum()
gdf_tract['Loss_2016'] = yearly_loss * gdf_tract['pop_2020'] / pop_total
gdf_tract['Loss_USD'] = utils.convert_USD(gdf_tract['Loss_2016'], 2016).values

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='EXH: Power Loss',
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
print("Finished calculating ESL for extreme heat due to power outage.")
