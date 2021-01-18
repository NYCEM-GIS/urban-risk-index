""" Calcualtes the fraction of shoreline that is natural."""

#%%% import packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from census import Census
from us import states
from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% load tracts
gdf_tract = utils.get_blank_tract()

#%% load shoreline
path_shoreline_gdb = params.PATHNAMES.at['RCA_ML_NS_shoreline_gbd', 'Value']
path_shoreline_layer = params.PATHNAMES.at['RCA_ML_NS_shoreline_layer', 'Value']
gdf_shoreline = gpd.read_file(path_shoreline_gdb, driver='FileGDB', layer=path_shoreline_layer)
gdf_shoreline = utils.project_gdf(gdf_shoreline)

#%% define fraction natural shoreline
gdf_tract['per_SL'] = np.ones(len(gdf_tract)) * np.nan

#%% calculate fraction of shoreline
buffer = params.PARAMS.at['search_buffer_for_natural_shoreline_ft', 'Value']
gdf_tract_buffer = gdf_tract.copy()
gdf_tract_buffer.geometry = gdf_tract.geometry.buffer(buffer)

#%%
for i, idx in enumerate(gdf_tract_buffer.index):
    this_tract = gdf_tract.loc[idx:idx, :]
    this_Stfid = gdf_tract.at[idx, 'Stfid']
    this_shoreline = gpd.overlay(gdf_shoreline, this_tract, how='intersection')
    if len(this_shoreline)>0:
        #get lengths
        this_shoreline['Length_ft'] = this_shoreline.geometry.length
        length_natural = this_shoreline.loc[this_shoreline['Type']=='3', 'Length_ft'].sum()
        length_total = this_shoreline['Length_ft'].sum()
        gdf_tract.at[idx, 'per_SL'] = (length_natural / length_total) * 100.
        #print('{} {}'.format(i, (length_natural / length_total) * 100.))

#%%fill with na values
gdf_tract.fillna(value={'per_SL':0}, inplace=True)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='per_SL', n_cluster=5)

#%% save as output
path_output = params.PATHNAMES.at['RCA_ML_NS_score', 'Value']
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
print("Finished calculating RCA factor: Place attachment.")





