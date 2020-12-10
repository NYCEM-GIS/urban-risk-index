""" calculate loss for CER due to ecosystem"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import math

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plot
utils.set_home()

#%% load tract with length of shoreline
path_shoreline = params.PATHNAMES.at['ESL_CER_CEHA_length', 'Value']
gdf_shoreline = gpd.read_file(path_shoreline)

#%% get erosion rate for each tract using parameters
list_locations = ['Rockaway_East', 'Rockaway_West', 'Rockaway_Middle',
                  'Coney_Island',
                  'Annandale_Staten_Island', 'Oakwood_Beach_Staten_Island', 'South_Shore_Staten_Island']
dict_erosion_rate_ft_yr = {}
for loc in list_locations:
    param_name = 'erosion_rate_' + loc + '_ft_yr'
    dict_erosion_rate_ft_yr[loc] = params.PARAMS.at[param_name, 'Value']
gdf_shoreline['erosion_rate_ft_yr'] = [dict_erosion_rate_ft_yr[x] for x in gdf_shoreline['CER_Zone']]

#%% open tract and merge shoreline data
gdf_tract = utils.get_blank_tract()
gdf_tract = gdf_tract[['BCT_txt', 'geometry']].merge(gdf_shoreline.drop(columns='geometry'), left_on='BCT_txt', right_on='BOROCT', how='left')

#set erosion rate and length to 0 for all other tracts
gdf_tract.fillna(value={'erosion_rate_ft_yr': 0}, inplace=True)
gdf_tract.fillna(value={'Shape_Leng': 0}, inplace=True)

#%% get cost parameter
value_per_ft2 = params.PARAMS.at['value_per_acre_marine_2015', 'Value'] / 43560.
value_per_ft2_2019 = utils.convert_USD(value_per_ft2, 2015)

#%% get number of foot-years of eroded land over 100 year period
#multiply by length of shoreline
gdf_tract['Eroded_area_ft2_years'] = np.arange(1, 101).sum() * gdf_tract['erosion_rate_ft_yr'] * gdf_tract['Shape_Leng']
gdf_tract['shoreline_value_lost'] = gdf_tract['Eroded_area_ft2_years'] * value_per_ft2_2019
#annualize loss
gdf_tract['Loss_USD'] = gdf_tract['shoreline_value_lost'] / 100.


#%% save as output
path_output = params.PATHNAMES.at['ESL_CER_ecosystem_loss', 'Value']
gdf_tract.to_file(path_output)

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
print("Finished calculating CER ecosystem loss.")