"""
calculate the total economic loss due to deaths from EXH
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load the event rate, death rate, and cost per death
path_events_per_year = params.PATHNAMES.at['EXH_events_per_year_tracts', 'Value']
gdf_events_per_year = gpd.read_file(path_events_per_year)
path_deaths_per_event = params.PATHNAMES.at['EXH_deaths_per_event', 'Value']
gdf_deaths_per_event = gpd.read_file(path_deaths_per_event)
value_life_2018 = params.PARAMS.at['value_of_stat_life_2015', 'Value']

#%% convert value of lost life to 2019 value
value_life = utils.convert_USD(value_life_2018, 2018)

#%% mere into single dataframe and calculate
gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
gdf_loss['deaths_year'] = gdf_loss['Heat_Event'] * gdf_loss['deaths_per']
gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * value_life

#%% save results in
path_results = params.PATHNAMES.at['EXH_ESL_deaths_per_year_tract', 'Value']
gdf_loss.to_file(path_results)

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_results)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating EXH loss due to excess deaths.")




