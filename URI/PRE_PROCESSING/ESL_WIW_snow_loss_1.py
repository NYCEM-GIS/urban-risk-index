""" estimate snow removal costs by inch"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_snow = PATHNAMES.ESL_WIW_snow_data
path_road = PATHNAMES.ESL_WIW_road_cover
# Output paths
path_output = PATHNAMES.ESL_WIW_loss_snow

#%% LOAD DATA
df_snow = pd.read_excel(path_snow, sheet_name='Duplicate')
df_road = pd.read_csv(path_road)

#%% tracts 
gdf_tract = utils.get_blank_tract()

#%%get costs based on 2018 dollars
df_snow.index = np.arange(2007, 2024)
df_snow['Snow Remove Cost'] = [utils.convert_USD(df_snow.at[idx, 'Snow Removal Cost'], idx) for idx in df_snow.index]
ave_cost_year = df_snow['Snow Remove Cost'].mean() * 1000000

#%% get length of road in each tract
df_road.index = np.arange(len(df_road))
df_road['BCT_txt'] = [str(df_road.at[idx, 'BCT_txt']) for idx in df_road.index]
gdf_tract = gdf_tract.merge(df_road, on='BCT_txt', how='left')


#%% distribute based on critical snow route length
gdf_tract['Loss_USD'] = ave_cost_year * gdf_tract['Critical_Route_Length'] / gdf_tract['Critical_Route_Length'].sum()

#%% save as output
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
