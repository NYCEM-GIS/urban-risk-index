""" get walkability data"""

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
folder_scratch = params.PATHNAMES.at['RCA_RC_WA_SCORE_scratch', 'Value']
if not os.path.exists(folder_scratch):
    os.mkdir(folder_scratch)
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_WA_score', 'Value']

#%% LOAD DATA
# gdf_block = gpd.read_file(path_block)
gdf_tract = utils.get_blank_tract()
path_walkscore = params.PATHNAMES.at['RCA_RC_WA_walkscore_csv', 'Value']
df_walkscore = pd.read_csv(path_walkscore)

#%% modify tracts a
# gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))
gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x

#%% use API to  get walkscore
# note the number of data downloads per day is limited.
if not os.path.exists(path_walkscore):
    for i, idx in enumerate(gdf_tract.index[1825:]):
        lat = str( np.round(gdf_tract['lat'].loc[idx], 5))
        lon = str(np.round(gdf_tract['lon'].loc[idx], 5))
        params_api = {'lat':lat, 'lon': lon,
                  'wsapikey':'279d12ceda7c0b0337fc51767356c243', 'format':'json',
                      'transit':1, 'bike':1}
        url = 'https://api.walkscore.com/score'
        #request data
        r = requests.get(url, params_api)
        data = r.json()
        try:
            walkscore = data['walkscore']
            gdf_tract.at[idx, 'walkscore'] = walkscore
        except:
            print("No walk score for idx {}".format(idx))
        try:
            bikescore = data['bike']['score']
            gdf_tract.at[idx, 'bikescore'] = bikescore
        except:
            print("No bike score for idx {}".format(idx))
        try:
            transitscore = data['transit']['score']
            gdf_tract.at[idx, 'transitscore'] = transitscore
        except:
            print("No bike score for idx {}".format(idx))
        print(idx)

        gdf_tract[['BCT_txt', 'walkscore', 'bikescore', 'transitscore', 'lat', 'lon']].to_csv(path_walkscore)

#%% modify walkscore and merge to tract shapefile
temp = df_walkscore['BCT_txt']
df_walkscore['BCT_txt'] = [str(x) for x in temp]
gdf_tract = gdf_tract.merge(df_walkscore[['BCT_txt', 'walkscore']], on='BCT_txt', how='left')

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='walkscore')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_WA: Walkability Score',
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
print("Finished calculating RCA factor: walkability score.")