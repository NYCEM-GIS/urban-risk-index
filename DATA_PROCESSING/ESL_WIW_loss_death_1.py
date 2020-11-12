""" deaths due to winter storms"""

#%% read packages
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


#%% count fatalities and injuries
deaths_per_year = params.PARAMS.at['WIW_deaths_per_year', 'Value']
loss_per_death_2015 = params.PARAMS.at['value_of_stat_life_2015', 'Value'] * deaths_per_year
loss_deaths_total = utils.convert_USD(loss_per_death_2015, 2015)

#%%  distribute loss by population
gdf_tract = utils.distribute_loss_by_pop(loss_deaths_total)

#%% save as output
path_output = params.PATHNAMES.at['ESL_WIW_loss_deaths', 'Value']
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
print("Finished calculating WIW death loss.")