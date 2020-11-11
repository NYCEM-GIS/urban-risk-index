""" calculate loss due to power outages
distributed by population
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load params
#number of outages hours per year across NYC due to heat
yearly_outage = params.PARAMS.at['EXH_outage_person_hrs_per_year', 'Value']
#loss per outage hour per person affected
loss_outage_hr = params.PARAMS.at['loss_hour_power_2015', 'Value']

#%%calculate total loss
yearly_loss = yearly_outage * loss_outage_hr

#%%  open tract
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)

#%% open population and join
path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
df_pop = pd.read_excel(path_population_tract, skiprows=5)
df_pop.dropna(inplace=True)
df_pop.rename(columns={2010:'pop_2010'}, inplace=True)
df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2010 DCP Borough Code'])) + str(int(df_pop.at[x,'2010 Census Tract'])).zfill(6) for x in df_pop.index]
gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2010']], on='BCT_txt', how='left')

#%% distribute cost to each tract by population
pop_total = gdf_tract['pop_2010'].sum()
gdf_tract['Loss_2015'] = yearly_loss * gdf_tract['pop_2010'] / pop_total
gdf_tract['Loss_USD'] = utils.convert_USD(gdf_tract['Loss_2015'], 2015).values

#%% save as output
path_output = params.PATHNAMES.at['ESL_EXH_loss_power', 'Value']
gdf_tract.to_file(path_output)

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
