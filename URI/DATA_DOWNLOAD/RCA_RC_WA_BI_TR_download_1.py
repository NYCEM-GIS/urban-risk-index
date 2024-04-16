import numpy as np
import pandas as pd
import os
import requests
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Output paths
path_walk_score = params.PATHNAMES.at['RCA_RC_WA_walkscore_csv', 'Value']

##%% load tracts to get centroid lat/longs
gdf_tract = utils.get_blank_tract()
gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x


#%% use API to  get walkscore
# note the number of data downloads per day is limited, and you must change the index (currently 1825:) to download more
for i, idx in enumerate(gdf_tract.index[1825:]):
    lat = str(np.round(gdf_tract['lat'].loc[idx], 5))
    lon = str(np.round(gdf_tract['lon'].loc[idx], 5))
    params_api = {
        'lat': lat,
        'lon': lon,
        'wsapikey': '279d12ceda7c0b0337fc51767356c243',
        'format': 'json',
        'transit': 1,
        'bike': 1}
    url = 'https://api.walkscore.com/score'
    # request data
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

    gdf_tract[['BCT_txt', 'walkscore', 'bikescore', 'transitscore', 'lat', 'lon']].to_csv(path_walk_score)