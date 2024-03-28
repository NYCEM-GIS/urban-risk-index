""" emergency medical facility"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_hospital = params.PATHNAMES.at['RCA_RC_EMA_raw', 'Value']
path_block = params.PATHNAMES.at['census_blocks', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_EM_score', 'Value']

#%% LOAD DATA
gdf_hospital = gpd.read_file(path_hospital)
gdf_block = gpd.read_file(path_block)

#%% modify data
gdf_hospital = utils.project_gdf(gdf_hospital)
gdf_hospital['OBJECTID'] = np.arange(len(gdf_hospital))

#%% modify tracts a
gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)

#%%get centroid
gdf_centroid = gdf_tract.copy()
gdf_centroid['geometry'] = gdf_tract['geometry'].centroid

#%% get for each pt get the nearest hospital for winter weather
gdf_hospital_subset = gdf_hospital.loc[gdf_hospital['HYPOTHERMI']==1, :]
pts3 = gdf_hospital_subset.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_hospital_subset.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_hospital_subset[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_HYPO'] = gdf_centroid.apply(lambda row: near(row.geometry), axis=1)

#%% repeat for distance to trauma
gdf_hospital_subset = gdf_hospital.loc[gdf_hospital['TRAUMA']==1, :]
pts3 = gdf_hospital_subset.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_hospital_subset.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_hospital_subset[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_TRAUMA'] = gdf_centroid.apply(lambda row: near(row.geometry), axis=1)

#%% repeat for distance to trauma
gdf_hospital_subset = gdf_hospital.loc[gdf_hospital['RECEIVING']==1, :]
pts3 = gdf_hospital_subset.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_hospital_subset.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_hospital_subset[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_RECEIVING'] = gdf_centroid.apply(lambda row: near(row.geometry), axis=1)

#%% write scores.  Set reverse=True because low distance values are better
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_HYPO', score_column='Score_WIW', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_EXH', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_RES', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_EMG', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_CRN', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_CST', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_CER', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_HIW', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_ERQ', reverse=True)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_FLD', reverse=True)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
list_abbrev = ['EXH', 'WIW', 'CST', 'CER', 'RES', 'EMG', 'CRN', 'HIW', 'ERQ', 'FLD']
for haz in list_abbrev:
    plotting.plot_notebook(gdf_tract, column='Score_'+haz, title='RCA_ML_MI: Emergency Capacity ({})'.format(haz),
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
print("Finished calculating RCA factor: emergency capacity.")
