""" load in cooling center factor """


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import sys
from sklearn.cluster import KMeans

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
gbd_cc = params.PATHNAMES.at["RCA_RC_CC_gdb", "Value"]
layer_cc = params.PATHNAMES.at["RCA_RC_CC_layer", "Value"]
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_CC_score', 'Value']

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
gdf_cc = gpd.read_file(gbd_cc, drive='FileGDB', layer=layer_cc)

#%% modify tract
gdf_tract['area_ft2'] = gdf_tract.geometry.area

#%%  add 1/2 mile buffer
gdf_cc_buffer = gdf_cc.copy()
gdf_cc_buffer['geometry'] = gdf_cc['geometry'].buffer(distance=5280/2.)

#%% create empty df to fill
df_fill = pd.DataFrame(columns = ['BCT_txt', 'Fraction_Covered'])

#%% loop through each buffer, and add BCT_txt and area filled to list
#print("Calculating.")
for i, idx in enumerate(gdf_cc_buffer.index):
    this_buffer = gdf_cc_buffer.loc[[idx]]
    #take intersection
    this_intersect = gpd.overlay(gdf_tract, this_buffer[['NYCEM_ID', 'geometry']], how='intersection')
    this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
    this_intersect['Fraction_Covered'] = np.minimum(this_intersect['area_intersect_ft2'] / this_intersect['area_ft2'], 1.0)
    #add to df_fill
    df_fill = df_fill.append(this_intersect[['BCT_txt', 'Fraction_Covered']])
#     if i % 50 == 0:
#         print(".")
# print('.')


#%% get the sum  by tract and join
df_sum = df_fill.groupby(by='BCT_txt').sum()
gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')
#gdf_tract = gdf_tract.to_file(r'.\1_RAW_INPUTS\ZZZ_SCRATCH\NYC_count.shp')

#fill nan with value 0
gdf_tract.fillna(0, inplace=True)

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Fraction_Covered')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_CC: Cooling Centers',
                       legend='Score', cmap='Blues', type='score')

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_results)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating RCA factor: Cooling Centers.")
