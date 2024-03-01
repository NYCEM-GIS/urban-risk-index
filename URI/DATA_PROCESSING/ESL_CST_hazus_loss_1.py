""" aggregatet hazus losses, annualized coastal storms"""

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

# %% open tract
gdf_tract = utils.get_blank_tract()

#%% open hazus data
path_gdb = params.PATHNAMES.at['ESL_CST_hazus_gdb', 'Value']
gdb_layer = params.PATHNAMES.at['ESL_CST_hazus_layer', 'Value']
df_hazus = gpd.read_file(path_gdb, driver='FileGDB', layer=gdb_layer)

#%% convert from 2007 to URI dollars, multiply by 1000
df_hazus['Loss_USD'] = utils.convert_USD(df_hazus.Hurricane_AnnualizedLoss , 2007) * 1000.

#%% merge to tract
gdf_tract = gdf_tract.merge(df_hazus[['Tract2010_STFID', 'Loss_USD']], left_on='geoid', right_on='Tract2010_STFID', how='left')

#%% save as output
path_output = params.PATHNAMES.at['ESL_CST_hazus_loss', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CST: HAZUS Loss',
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
print("Finished calculating CST Hazus loss.")