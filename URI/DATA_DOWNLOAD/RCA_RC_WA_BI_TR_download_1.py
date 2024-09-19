import numpy as np
import requests
import URI.MISC.utils_1 as utils
utils.set_home()

#%% EXTRACT PARAMETERS
# Output paths
path_walk_score = r'C:\Users\hsprague\miniconda\URI_Calculator_v1_1\1_RAW_INPUTS\RCA_WALKSCORE\walkscore_1.csv'

##%% load tracts to get centroid lat/longs
gdf_tract = utils.get_blank_tract()
gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x
gdf_tract[['walkscore', 'bikescore', 'transitscore']] = 0

#%% use API to  get walkscore
# note the number of data downloads per day is limited, and you must change the index (currently 1825:) to download more
for i, idx in enumerate(gdf_tract.index):
    lat = str(np.round(gdf_tract['lat'].loc[idx], 5))
    lon = str(np.round(gdf_tract['lon'].loc[idx], 5))
    params_api = {
        'lat': lat,
        'lon': lon,
        'wsapikey': '67cbd2d08447b6d1d2c51a14deeace3c',
        'format': 'json',
        'transit': 1,
        'bike': 1}
    url = 'https://api.walkscore.com/score'
    # request data
    r = requests.get(url, params_api, verify=False)
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
        print("No transit score for idx {}".format(idx))

    gdf_tract[['BCT_txt', 'walkscore', 'bikescore', 'transitscore', 'lat', 'lon']].to_csv(path_walk_score)