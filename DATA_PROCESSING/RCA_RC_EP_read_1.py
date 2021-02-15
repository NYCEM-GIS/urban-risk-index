""" emergency medical facility"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% get tracts
gdf_tract = utils.get_blank_tract()

#%% load data
path_center = params.PATHNAMES.at['RCA_RC_EP_raw', 'Value']
gdf_center = gpd.read_file(path_center)
gdf_center = utils.project_gdf(gdf_center)


#%%get centroid
gdf_centroid = gdf_tract.copy()
gdf_centroid['geometry'] = gdf_tract['geometry'].centroid

#%% get for each pt get the nearest hospital for winter weather
pts3 = gdf_center.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_center.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_center[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_Center'] = gdf_centroid.apply(lambda row: near(row.geometry), axis=1)

#%% write scores
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_Center', score_column='Score', reverse=True)

#%%assign 5 to everything in zone X of hurrican evac zone
path_zone = params.PATHNAMES.at['RCA_RC_EP_evac_zones', 'Value']
gdf_zone = gpd.read_file(path_zone)
gdf_zone = gdf_zone.to_crs(gdf_tract.crs)
gdf_zone = gdf_zone.loc[gdf_zone.hurricane=='X']
gdf_tract_sjoin = gpd.sjoin(gdf_tract, gdf_zone, how='inner', op='within')
gdf_tract_sjoin['Is_inland'] = 1
gdf_tract= gdf_tract.merge(gdf_tract_sjoin[['BCT_txt', 'Is_inland']], how='left', on='BCT_txt')
gdf_tract.loc[gdf_tract.Is_inland==1, 'Score'] = 5

#%%
fig = plt.figure()
ax = fig.add_subplot(111)
gdf_tract.plot(ax=ax)
gdf_zone.plot(ax=ax, color='red')
plt.show()


#%% save as output
path_output = params.PATHNAMES.at['RCA_RC_EP_score', 'Value']
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
print("Finished calculating RCA factor: emergency capacity.")
