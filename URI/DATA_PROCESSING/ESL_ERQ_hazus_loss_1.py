""" incorporate flooding damaage due to coastal storms"""

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
#%% EXTRACT PARAMETERS
# Input paths
path_erq_hazus = r'.\1_RAW_INPUTS\ERQ_HAZUS\Earthquakes (5.2M)\results.shp'
# Output paths
path_output = params.PATHNAMES.at['ESL_ERQ_hazus_loss', 'Value']

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)
# df_hazus = gpd.read_file(path_gbd, driver='FileGBD', layer=layer_gbd)
df_hazus = gpd.read_file(path_erq_hazus)


#%% use tract to merge hazus data to tract
gdf_tract = gdf_tract.merge(df_hazus[['tract', 'EconLoss']], left_on='geoid', right_on='tract', how='left')

#%% convert to current USD
gdf_tract.EconLoss = utils.convert_USD(gdf_tract.EconLoss.values, 2018)

#%% total loss is in USD 1000.... convert
gdf_tract['Loss_USD'] = gdf_tract['EconLoss'] * 1000.

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='ERQ: HAZUS Loss',
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
print("Finished calculating ERQ Hazus loss.")