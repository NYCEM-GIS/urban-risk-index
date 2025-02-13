""" incorporate flooding damage due to coastal storms"""

#%% read packages
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
from URI.PARAMS.params import PARAMS 
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_flood_bronx = PATHNAMES.ESL_CSF_hazus_bronx
path_flood_kings = PATHNAMES.ESL_CSF_hazus_kings
path_flood_manhattan = PATHNAMES.ESL_CSF_hazus_manhattan
path_flood_queens = PATHNAMES.ESL_CSF_hazus_queens
path_flood_richmond = PATHNAMES.ESL_CSF_hazus_richmond
# Output paths
path_output = PATHNAMES.ESL_FLD_hazus_loss

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
gdf_flood_bronx = gpd.read_file(path_flood_bronx)
gdf_flood_kings = gpd.read_file(path_flood_kings)
gdf_flood_manhattan = gpd.read_file(path_flood_manhattan)
gdf_flood_queens = gpd.read_file(path_flood_queens)
gdf_flood_richmond = gpd.read_file(path_flood_richmond)

#%% Flood Data Preprocessing
gdf_flood_data_list = [gdf_flood_bronx, gdf_flood_kings, gdf_flood_manhattan, gdf_flood_queens, gdf_flood_richmond]
gdf_flood_data_by_tract_list = []

for fld_file in gdf_flood_data_list:
    fld_file['tract'] = fld_file['block'].str[0:11]  # Tract ID is equal to the first 11 digits of the block id
    fld_file_by_tract = fld_file[['tract', 'EconLoss', 'geometry']].dissolve(by='tract', as_index=False, aggfunc='sum')
    gdf_flood_data_by_tract_list.append(fld_file_by_tract)

gdf_flood = gpd.GeoDataFrame(pd.concat(gdf_flood_data_by_tract_list, ignore_index=True))
gdf_flood.rename(columns={'EconLoss': 'Loss_USD'}, inplace=True)

##%% convert from 2018 dollars
gdf_flood.Loss_USD = utils.convert_USD(gdf_flood.Loss_USD.values, 2018)

#%% merge with tracts
gdf_tract = gdf_tract.merge(gdf_flood[['tract', 'Loss_USD']], left_on='geoid', right_on=['tract'], how='left')
gdf_tract['Loss_USD'] = gdf_tract['Loss_USD'].fillna(0)

#%% save as output
gdf_tract.to_file(path_output)


#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CSF: Building Damage',
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
print("Finished calculating CSF Building Damage.")