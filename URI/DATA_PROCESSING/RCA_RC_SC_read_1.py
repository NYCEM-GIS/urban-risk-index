""" shelter capacity"""
#need to handle nan values

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract(add_pop=True)
gdf_tract['area_ft2'] = gdf_tract.geometry.area
gdf_tract['pop_2010_density'] = gdf_tract['pop_2010'] / gdf_tract['area_ft2']

#%% load shelter capacity data
path_sc_gbd = params.PATHNAMES.at['RCA_RC_SC_raw', 'Value']
layer_sc = params.PATHNAMES.at['RCA_RC_SC_layer', 'Value']
gdf_sc = gpd.read_file(path_sc_gbd, driver='FileGBD', layer=layer_sc)
gdf_sc = gdf_sc.to_crs(crs=gdf_tract.crs)
#convert null to 0 values
gdf_sc.fillna(value={'Long_term_capacity':0}, inplace=True)

#%% allocate shelter beds to tracts based on population.
#add column to count allocated shelter beds
gdf_tract['LT_capacity_count'] = np.zeros(len(gdf_tract))
#loop through each shelter and assign capacity to tracts
buffer_radius = params.PARAMS.at['search_buffer_for_shelter_capacity_ft', 'Value']
for i, idx in enumerate(gdf_sc.index):
    this_shelter = gdf_sc.loc[idx:idx, :].copy()
    this_capacity = this_shelter.at[idx, 'Long_term_capacity']
    this_shelter.loc[idx, 'geometry'] = this_shelter.loc[idx, 'geometry'].buffer(distance=buffer_radius)
    this_shelter.loc[idx, 'geometry'] = this_shelter.loc[idx, 'geometry']
    #get intersecting tracts
    gdf_intersect = gpd.overlay(gdf_tract, this_shelter, how='intersection')
    #eliminate
    #get_intersection_areas
    gdf_intersect['area_ft2'] = gdf_intersect.geometry.area
    gdf_intersect['population'] = gdf_intersect['area_ft2'] * gdf_intersect['pop_2010_density']
    gdf_intersect['capacity_allocation'] = this_capacity * gdf_intersect['population'] / gdf_intersect['population'].sum()
    #loop through and add allocation to each tract
    for j, jdx in enumerate(gdf_intersect.index):
        this_Stfid = gdf_intersect.at[jdx, 'Stfid']
        gdf_tract.loc[gdf_tract['Stfid']==this_Stfid, 'LT_capacity_count'] += gdf_intersect.at[jdx, 'capacity_allocation']
    #if i % 10 == 0: print("{}".format(i))

#%% calculate capacity per 1000
gdf_tract['capacity_allocation_per_1000'] = gdf_tract['LT_capacity_count'] * 1000. / gdf_tract['pop_2010']
#set null values (with 0 population ) to 0
gdf_tract.fillna(value={'capacity_allocation_per_1000':0}, inplace=True)

#%% calculate score
#need to handle missing data
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='capacity_allocation_per_1000')

#%% save as output
path_output = params.PATHNAMES.at['RCA_RC_SC_score', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_HI: Median Household Income',
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
print("Finished calculating RCA factor: Median Household Income")