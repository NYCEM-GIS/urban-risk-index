""" get bikability score"""

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
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_block = params.PATHNAMES.at['census_blocks', 'Value']
path_transitscore = params.PATHNAMES.at['RCA_RC_TR_transitscore_csv', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_TR_score', 'Value']

#%% LOAD DATA
# gdf_block = gpd.read_file(path_block)
gdf_block = utils.get_blank_tract()

df_transitscore  = pd.read_csv(path_transitscore)

#%% modify tracts a
gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x


#%% modify walkscore and merge to tract shapefile
temp = df_transitscore['BCT_txt']
df_transitscore['BCT_txt'] = [str(x) for x in temp]
gdf_tract = gdf_tract.merge(df_transitscore[['BCT_txt', 'transitscore']], on='BCT_txt', how='left')

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='transitscore')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_TR: Transit Score',
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
print("Finished calculating RCA factor: transit score.")