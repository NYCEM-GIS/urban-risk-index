""" calculate loss for CER due to ecosystem"""

import numpy as np
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_shoreline = PATHNAMES.ESL_CER_CEHA_length
# Params
value_per_ft2 = PARAMS['value_per_acre_marine'].value / 43560.
list_locations = ['Rockaway_East', 'Rockaway_West', 'Rockaway_Middle',
                  'Coney_Island',
                  'Annandale_Staten_Island', 'Oakwood_Beach_Staten_Island', 'South_Shore_Staten_Island']
dict_erosion_rate_ft_yr = {}
for loc in list_locations:
    param_name = 'erosion_rate_' + loc + '_ft_yr'
    dict_erosion_rate_ft_yr[loc] = PARAMS[param_name].value
# Output Paths
path_output = PATHNAMES.ESL_CER_ecosystem_loss


#%% LOAD DATA
gdf_shoreline = gpd.read_file(path_shoreline)
gdf_tract = utils.get_blank_tract()

#%% get erosion rate for each tract using parameters
gdf_shoreline['erosion_rate_ft_yr'] = [dict_erosion_rate_ft_yr[x] for x in gdf_shoreline['CER_Zone']]

#%% open tract and merge shoreline data
gdf_tract = gdf_tract[['BCT_txt', 'geometry']].merge(gdf_shoreline.drop(columns='geometry'), left_on='BCT_txt', right_on='BOROCT', how='left')

#set erosion rate and length to 0 for all other tracts
gdf_tract.fillna(value={'erosion_rate_ft_yr': 0}, inplace=True)
gdf_tract.fillna(value={'Shape_Leng': 0}, inplace=True)

#%% get cost parameter
value_per_ft2_2019 = utils.convert_USD(value_per_ft2, 2016)

#%% get number of foot-years of eroded land over 100 year period
#multiply by length of shoreline
gdf_tract['Eroded_area_ft2_years'] = np.arange(1, 101).sum() * gdf_tract['erosion_rate_ft_yr'] * gdf_tract['Shape_Leng']
gdf_tract['shoreline_value_lost'] = gdf_tract['Eroded_area_ft2_years'] * value_per_ft2_2019
#annualize loss
gdf_tract['Loss_USD'] = gdf_tract['shoreline_value_lost'] / 100.


#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CER: Ecosystem Loss',
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
print("Finished calculating CER ecosystem loss.")