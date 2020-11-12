""" calculate loss for CER due to ecosystem"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load tract with length of shoreline
path_tract = params.PATHNAMES.at['ESL_CER_CEHA_length', 'Value']
gdf_tract = gpd.read_file(path_tract)
gdf_tract = utils.project_gdf(gdf_tract)

#%% get cost parameters
erosion_year_ft = params.PARAMS.at['average coastal erosion rate_m', 'Value'] * 3.281
value_per_ft2 = params.PARAMS.at['value_per_acre_marine_2015', 'Value'] / 43560.

value_per_ft2_2019 = utils.convert_USD(value_per_ft2, 2015)

#%% make dataframe to estimate cost over next 100 years
df_cost = pd.DataFrame(index=np.arange(1, 101))
df_cost['area_lost_per_ft_shore'] =df_cost.index + np.arange(1, 101)* erosion_year_ft
df_cost['value_lost_per_ft_shore'] = df_cost['area_lost_per_ft_shore'] * value_per_ft2_2019
total_value_per_ft_shore_per_year = df_cost['value_lost_per_ft_shore'].sum()/100.
# assume discount rate equals inflation
#divide by 100 to annualize

#%% caluclate loss per tract
gdf_tract['Loss_USD'] = gdf_tract['Length'] * total_value_per_ft_shore_per_year

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