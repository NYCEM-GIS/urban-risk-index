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
utils.set_home()


#%% load data
path_hospital = params.PATHNAMES.at['RCA_RC_EMA_raw', 'Value']
gdf_hospital = gpd.read_file(path_hospital)
gdf_hospital = utils.project_gdf(gdf_hospital)
gdf_hospital['OBJECTID'] = np.arange(len(gdf_hospital))

#%% load tracts a
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
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
gdf_tract['Distance_HYPO'] = gdf_tract.apply(lambda row: near(row.geometry), axis=1)

#%% repeat for distance to trauma
gdf_hospital_subset = gdf_hospital.loc[gdf_hospital['TRAUMA']==1, :]
pts3 = gdf_hospital_subset.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_hospital_subset.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_hospital_subset[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_TRAUMA'] = gdf_tract.apply(lambda row: near(row.geometry), axis=1)

#%% repeat for distance to trauma
gdf_hospital_subset = gdf_hospital.loc[gdf_hospital['RECEIVING']==1, :]
pts3 = gdf_hospital_subset.geometry.unary_union
def near(point, pts=pts3):
    # find the nearest point and return the corresponding Place value
    nearest = gdf_hospital_subset.geometry == nearest_points(point, pts)[1]
    distance = point.distance(gdf_hospital_subset[nearest]['geometry'].iloc[0])
    return distance
gdf_tract['Distance_RECEIVING'] = gdf_tract.apply(lambda row: near(row.geometry), axis=1)

#%% write scores
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_HYPO', score_column='Score_WIW')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_EXH')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_RES')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_EMG')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_CST')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_CER')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_HIW')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_ERQ')
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_FLD')

#%% save as output
path_output = params.PATHNAMES.at['RCA_RC_EMA_score', 'Value']
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
