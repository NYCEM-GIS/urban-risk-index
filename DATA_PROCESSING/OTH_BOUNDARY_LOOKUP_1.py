""" create lookup table to move from one boundary to another"""

"""
import ac data
convert into tract data with correct projection
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()


#%% get tract population
gdf_tract = utils.get_blank_tract(add_pop=True)
gdf_tract['area_tract'] = gdf_tract.geometry.area

#%% get boundary intersect
path_community = params.PATHNAMES.at['BOUNDARY_community', 'Value']
gdf_community = gpd.read_file(path_community)
gdf_community = utils.project_gdf(gdf_community)
gdf_community['area_community'] = gdf_community.geometry.area

#%% get union
gdf_union = gpd.overlay(gdf_tract, gdf_community, how='union')
gdf_union['area_union'] = gdf_union.geometry.area
gdf_union['frac_tract_area'] = gdf_union['area_union'] / gdf_union['area_tract']


#%% group and keep only the largest area
#idx = df.groupby(['Mt'])['count'].transform(max) == df['count']
idx = gdf_union.groupby(['Stfid'])['frac_tract_area'].transform(max)==gdf_union['frac_tract_area']
gdf_key = gdf_union[idx]

#%% keep only most important columns
df_key = gdf_key[['Stfid', 'NEIGHBORHO', 'boro_cd', 'BOROCODE']].copy()

#%% remname
df_key.rename(columns={'NEIGHBORHO':'NeighCode', 'boro_cd':'CommCode', 'BOROCODE':'BoroCode'}, inplace=True)

#%% merge with tract geodatabase
gdf_tract = gdf_tract.merge(df_key, on='Stfid', how='left')

#%% open neighborhood to get neighborhood name
path_neigh = params.PATHNAMES.at['BOUNDARY_neighborhood', 'Value']
gdf_neigh = gpd.read_file(path_neigh)
gdf_tract = gdf_tract.merge(gdf_neigh[['ntacode', 'ntaname']], left_on='NeighCode', right_on='ntacode', how='left')

#%% save
path_lookup = params.PATHNAMES.at['BOUNDARY_lookup', 'Value']
gdf_tract.to_file(path_lookup)