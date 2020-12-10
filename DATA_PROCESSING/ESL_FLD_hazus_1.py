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

#%% load hazus data
path_flood = params.PATHNAMES.at['ESL_FLD_hazus', 'Value']
gdf_flood = gpd.read_file(path_flood)

#%% get flood loss total
gdf_flood['Loss_USD'] = gdf_flood['Sum_BldgLo'] + gdf_flood['Sum_Cont_1'] + gdf_flood['Sum_Invent']

#%% merge with tracts
gdf_tract = gdf_tract.merge(gdf_flood[['Stfid', 'Loss_USD']], left_on='Stfid', right_on=['Stfid'], how='left')

#%% save as output
path_output = params.PATHNAMES.at['ESL_FLD_hazus_loss', 'Value']
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
print("Finished calculating FLD Hazus loss.")