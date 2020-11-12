""" calculate storm related deaths from the HH&C database"""


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

#%% open event types - note 6 is coastal storm
path_eventtypes = params.PATHNAMES.at['HHC_eventtypes', 'Value']
df_types = pd.read_excel(path_eventtypes)

#%% open storm events with types
path_stormeventtypes = params.PATHNAMES.at['HHC_stormeventtypes', 'Value']
df_stormevents = pd.read_excel(path_stormeventtypes)
#only keep storms of event type 7
df_coastalevents = df_stormevents.loc[df_stormevents['EventTypeId']==6, :]

#%% find these 32 events in
path_storms = params.PATHNAMES.at['stormevents_table', 'Value']
df_storms = pd.read_excel(path_storms)
df_storms.index= df_storms['Id']
id_coastal = [df_coastalevents.at[idx, 'StormEventId'] for idx in df_coastalevents.index]
df_storms_cst = df_storms.loc[id_coastal, :]

#%% cut off data
start_date = params.HARDCODED.at['hhc_event_count_start_date', 'Value']
end_date = params.HARDCODED.at['hhc_event_count_end_date', 'Value']
df_storms_cst = df_storms_cst.loc[df_storms_cst['StartDate']>start_date]
df_storms_cst = df_storms_cst.loc[df_storms_cst['EndDate']<end_date]

#%% count fatalities and injuries
n_years = (end_date - start_date).days / 365.25
n_deaths = df_storms_cst['Fatalities'].sum() / n_years
n_injuries = df_storms_cst['Injuries'].sum() / n_years
#no injuries
loss_deaths_2015 = params.PARAMS.at['value_of_stat_life_2015', 'Value'] * n_deaths
loss_deaths_total = utils.convert_USD(loss_deaths_2015, 2015)

#%%  distribute loss by population
gdf_tract = utils.distribute_loss_by_pop(loss_deaths_total)

#%% save as output
path_output = params.PATHNAMES.at['ESL_CST_deaths_loss', 'Value']
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
print("Finished calculating CST death loss.")