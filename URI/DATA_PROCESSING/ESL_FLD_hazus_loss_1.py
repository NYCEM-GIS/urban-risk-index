""" incorporate flooding damage due to coastal storms"""

#%% read packages
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_flood_bronx = r".\1_RAW_INPUTS\Hazus - Loss Estimation Data\Coastal Flooding\Coastal Flooding 100 Year\Bronx\Bronx_100PFIRM\results.shp"
path_flood_kings = r".\1_RAW_INPUTS\Hazus - Loss Estimation Data\Coastal Flooding\Coastal Flooding 100 Year\Kings\Kings_100PFIRM\results.shp"
# Output paths
path_output = params.PATHNAMES.at['ESL_FLD_hazus_loss', 'Value']

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
gdf_flood_bronx = gpd.read_file(path_flood_bronx)
gdf_flood_kings = gpd.read_file(path_flood_kings)
gdf_flood_manhattan = gpd.read_file(r".\1_RAW_INPUTS\Hazus - Loss Estimation Data\Coastal Flooding\Coastal Flooding 100 Year\New York\NewYork_100PFIRM\results.shp")
gdf_flood_queens = gpd.read_file(r".\1_RAW_INPUTS\Hazus - Loss Estimation Data\Coastal Flooding\Coastal Flooding 100 Year\Queens\Queens_100PFIRM\results.shp")
gdf_flood_richmond = gpd.read_file(r".\1_RAW_INPUTS\Hazus - Loss Estimation Data\Coastal Flooding\Coastal Flooding 100 Year\Richmond\Richmond_100PFIRM\results.shp")

#%% Flood Data Preprocessing
print(type(gdf_flood_bronx))
gdf_flood_data_list = [gdf_flood_bronx, gdf_flood_kings, gdf_flood_manhattan, gdf_flood_queens, gdf_flood_richmond]
gdf_flood_data_by_tract_list = []
for fld_file in gdf_flood_data_list:
    fld_file['tract'] = fld_file['block'][:11]  # Tract ID is equal to the first 11 digits of the block id
    fld_file_by_tract = fld_file[['tract', 'EconLoss', 'geometry']].dissolve(by='tract', as_index=False)
    gdf_flood_data_by_tract_list.append(fld_file_by_tract)

gdf_flood = gpd.GeoDataFrame(pd.concat(gdf_flood_data_by_tract_list, ignore_index=True))
gdf_flood.rename(columns={'EconLoss': 'Loss_USD'}, inplace=True)

##%% convert from 2018 dollars
gdf_flood.Loss_USD = utils.convert_USD(gdf_flood.Loss_USD.values, 2018)

#%% merge with tracts
gdf_tract = gdf_tract.merge(gdf_flood[['tract', 'Loss_USD']], left_on='geoid', right_on=['tract'], how='left')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='FLD: HAZUS Loss',
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
print("Finished calculating FLD Hazus loss.")