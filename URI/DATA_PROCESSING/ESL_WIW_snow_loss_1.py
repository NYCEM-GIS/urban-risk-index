""" estimate snow removal costs by inch"""

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

#%% load tract

#%% load tracts a
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))
gdf_tract['area_ft2'] = gdf_tract.geometry.area

#%% load snow removal costs
path_snow = params.PATHNAMES.at['ESL_WIW_snow_data', 'Value']
df_snow = pd.read_excel(path_snow, sheet_name='Duplicate')

#%%get costs based on 2018 dollars
df_snow.index = np.arange(2007, 2019)
df_snow['Snow Remove Cost 2019'] = [utils.convert_USD(df_snow.at[idx, 'Snow Removal Cost'], idx) for idx in df_snow.index]
ave_cost_year = df_snow['Snow Remove Cost 2019'].mean() * 1000000

#%% get area of road in each tract
path_road = params.PATHNAMES.at['ESL_WIW_road_cover', 'Value']
df_road = pd.read_csv(path_road)
df_road.index = np.arange(len(df_road))
df_road['BCT_txt'] = [str(df_road.at[idx, 'BCT_TXT']) for idx in df_road.index]
gdf_tract = gdf_tract.merge(df_road, on='BCT_txt', how='left')

#%% distribute based on area
gdf_tract['road_area_ft2'] = gdf_tract['area_ft2'] * gdf_tract['MEAN']
gdf_tract['Loss_USD'] = ave_cost_year * gdf_tract['road_area_ft2'] / gdf_tract['road_area_ft2'].sum()

#%% save as output
path_output = params.PATHNAMES.at['ESL_WIW_loss_snow', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='WIW: Snow Removal Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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
print("Finished calculating  ESL WIW snow removal loss.")
