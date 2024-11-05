""" estimate cost of dislocated residents from coastal storms """

#%% read packages
import numpy as np
import geopandas as gpd
import os
from rasterstats import zonal_stats
import URI.MISC.utils_1 as utils
import URI.PARAMS.path_names as PATHNAMES
import time
utils.set_home()
t0 = time.time()
#%% EXTRACT PARAMETERS
# Input paths
path_footprint = PATHNAMES.ESL_CST_building_footprints

# Output paths
path_footprint_depths = PATHNAMES.ESL_CST_building_footprints_depth

#%% make copy of building footprints  with hurricane depths
# open and project footprint shapefile
print('reading footprints...')
gdf_footprint = gpd.read_file(path_footprint)
print('projecting footprints...')
gdf_depths = utils.project_gdf(gdf_footprint)

# loop through 4 cat types
for cat in np.arange(1, 5):
    t1 = time.time()
    print(".....adding data for category {} storms".format(cat))
    # get path to depth raster
    path_C = getattr(PATHNAMES,'ESL_CST_SLOSH_C{}'.format(cat))
    # perform zonal stats
    dict_c = zonal_stats(path_footprint, path_C, stats="max")
    # join results to footprint
    gdf_depths['C{}_depth'.format(cat)] = [x['max'] for x in dict_c]
    t2 = time.time()
    print(f'  cat {cat} completed in {(t2 - t1)/60:0.1f} minutes')
# save results
gdf_depths.to_file(path_footprint_depths)
print(f'Done in {(t2 - t0)/60:0.1f} minutes')

