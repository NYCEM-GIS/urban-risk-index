""" Calculates the fraction of shoreline that is natural."""

#%%% import packages
import numpy as np
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_shoreline = params.PATHNAMES.at['RCA_ML_NS_shoreline', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_ML_NS_score', 'Value']
# Params
buffer = params.PARAMS.at['search_buffer_for_natural_shoreline_ft', 'Value']

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
path_shoreline_gdb = os.path.dirname(path_shoreline)
path_shoreline_layer = os.path.basename(path_shoreline)
gdf_shoreline = gpd.read_file(path_shoreline_gdb, driver='FileGDB', layer=path_shoreline_layer)
gdf_shoreline = utils.project_gdf(gdf_shoreline)

#%% define fraction natural shoreline
gdf_tract['per_SL'] = np.ones(len(gdf_tract)) * np.nan

#%% calculate fraction of shoreline
gdf_tract_buffer = gdf_tract.copy()
gdf_tract_buffer.geometry = gdf_tract.geometry.buffer(buffer)

#%%
for i, idx in enumerate(gdf_tract_buffer.index):
    this_tract = gdf_tract.loc[idx:idx, :]
    this_shoreline = gpd.overlay(gdf_shoreline, this_tract, how='intersection')
    if len(this_shoreline) > 0:
        # get lengths
        this_shoreline['Length_ft'] = this_shoreline.geometry.length
        length_natural = this_shoreline.loc[this_shoreline['Type'] == '3', 'Length_ft'].sum()
        length_total = this_shoreline['Length_ft'].sum()
        gdf_tract.at[idx, 'per_SL'] = (length_natural / length_total) * 100.

#%% fill with na values
gdf_tract.fillna(value={'per_SL': 0}, inplace=True)

#%% convert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='per_SL', n_cluster=5)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_ML_NS: Presence of Natural Shoreline',
                       legend='Score', cmap='Blues', type='score')

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
print("Finished calculating RCA factor: Presence of Natural Shoreline.")





