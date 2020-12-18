""" incorporate flooding damaage due to coastal storms"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% get tract
gdf_tract = utils.get_blank_tract()

#%% load hazus
path_gbd = params.PATHNAMES.at['ESL_ERQ_hazus_gbd', 'Value']
layer_gbd = params.PATHNAMES.at['ESL_ERQ_hazus_layer', 'Value']
df_hazus = gpd.read_file(path_gbd, driver='FileGBD', layer=layer_gbd)

#%% use tract to merge hazus data to tract
gdf_tract = gdf_tract.merge(df_hazus[['Tract', 'TotalLoss']], left_on='Stfid', right_on='Tract', how='left')

#%% convert to current USD
gdf_tract.TotalLoss = utils.convert_USD(gdf_tract.TotalLoss.values, 2018)

#%% total loss is in USD 1000.... convert
gdf_tract['Loss_USD'] = gdf_tract['TotalLoss'] * 1000.

#%% save as output
path_output = params.PATHNAMES.at['ESL_ERQ_hazus_loss', 'Value']
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
print("Finished calculating ERQ Hazus loss.")