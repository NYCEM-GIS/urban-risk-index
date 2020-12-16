""" get bikability score"""

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
utils.set_home()


#%% load tracts a
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x


#%% load walkscore and merge to tract shapefile
path_bikescore = params.PATHNAMES.at['RCA_RC_BI_bikescore_csv', 'Value']
df_bikescore  = pd.read_csv(path_bikescore)
temp = df_bikescore['BCT_txt']
df_bikescore['BCT_txt'] = [str(x) for x in temp]
gdf_tract = gdf_tract.merge(df_bikescore[['BCT_txt', 'bikescore']], on='BCT_txt', how='left')

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='bikescore')

#%% save as output
path_output = params.PATHNAMES.at['RCA_RC_BI_score', 'Value']
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
print("Finished calculating RCA factor: bikability.")