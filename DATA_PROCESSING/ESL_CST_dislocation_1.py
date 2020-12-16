""" estimate cost of dislocated residents from coastal storms """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests
import rasterio
from rasterstats import zonal_stats

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% get traCT
gdf_tract = utils.get_blank_tract()

#%% make scratch folder if doesn't already exist
folder_scratch = params.PATHNAMES.at['ESL_CST_loss_dislocation_scratch', 'Value']
if not os.path.exists(folder_scratch):
    os.mkdir(folder_scratch)

#%% import building footprints path name
path_footprint = params.PATHNAMES.at['ESL_CST_building_footprints', 'Value']

#%% make copy of building footprints  with hurricane depths, if it doesn't already exist
path_footprint_depths = os.path.join(folder_scratch, 'NYC_Buildings_composite_20200110_flood_depths_1.shp')
if not os.path.exists(path_footprint_depths):
    #open and project footprint shapefile
    gdf_footprint = gpd.read_file(path_footprint, driver='FileGBD', layer='NYC_Buildings_composite_20200110')
    gdf_footprint = gdf_footprint.to_crs(gdf_tract.crs)
    #loop through 4 cat types
    for cat in np.arange(1,5):
        print(".....adding data for category {} storms".format(cat))
        #get path to depth raster
        path_C = params.PATHNAMES.at['ESL_CST_SLOSH_C{}'.format(cat), 'Value']
        #save footprint file to temp location
        path_temp = os.path.join(folder_scratch, 'temp.shp')
        gdf_footprint.to_file(path_temp)
        #perform zonal stats
        dict_c = zonal_stats(path_temp, path_C, stats="mean max")
        #join results to footprint
        gdf_footprint['C{}_depth'.format(cat)] = [x['max'] for x in dict_c]
    #save results
    gdf_footprint.to_file(path_footprint_depths)
    print("Done")

#%%











