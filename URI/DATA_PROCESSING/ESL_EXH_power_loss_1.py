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
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_block = params.PATHNAMES.at['census_blocks', 'Value']
path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
# Params
yearly_outage = params.PARAMS.at['EXH_outage_person_hrs_per_year', 'Value']
loss_outage_hr = params.PARAMS.at['loss_day_power', 'Value'] / 24.
# Output paths
path_output = params.PATHNAMES.at['ESL_EXH_loss_power', 'Value']

#%% LOAD DATA
gdf_block = gpd.read_file(path_block)
df_pop = pd.read_excel(path_population_tract, skiprows=5)

#%%calculate total loss
yearly_loss = yearly_outage * loss_outage_hr

#%%  open tract
gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)

#%% open population and join
df_pop.dropna(inplace=True, subset=['2020 DCP Borough Code', '2020 Census Tract'])
df_pop.rename(columns={2020:'pop_2020'}, inplace=True)
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
