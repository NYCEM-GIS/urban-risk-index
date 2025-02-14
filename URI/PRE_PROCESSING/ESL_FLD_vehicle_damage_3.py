import geopandas as gpd

#%% read packages
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()
#%% EXTRACT PARAMETERS
# Input paths
block_shapefile = PATHNAMES.ESL_FLD_vehicle_damage_block
# Output paths
path_output = PATHNAMES.ESL_FLD_vehicle_damage_tract



# Load the block level shapefile
blocks = gpd.read_file(block_shapefile)

# Ensure the block shapefile has a column for vehicle damages and tract IDs
if 'vehicle_damage' not in blocks.columns or 'tract_id' not in blocks.columns:
    raise ValueError("Shapefile must contain 'vehicle_damage' and 'tract_id' columns")

# Aggregate vehicle damages to the tract level
tracts = blocks.dissolve(by='tract_id', aggfunc='sum')

# Save the aggregated data to a new shapefile
tracts.to_file(path_output)

