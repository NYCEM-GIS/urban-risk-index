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

#%% load gree service data
path_tree = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\TreeServices.xlsx'
df_tree = pd.read_excel(path_tree, parse_dates=['DateInitiated', 'DateCreated'])

#%%  review data to figure out data structure
df_test  = df_tree.copy()
df_test  = df_test.loc[df_test.DateInitiated > '2012/10/29', :]
df_test  = df_test.loc[df_test.DateInitiated < '2012/10/30', :]
df_test = df_test.sort_values(by='DateInitiated')

#%%% visualize the results
gdf_tract = utils.get_blank_tract()
df_test = df_test.loc[df_test.Long != 0, :]
gdf_test = gpd.GeoDataFrame(df_test, geometry=gpd.points_from_xy(df_test.Long, df_test.Lat))
gdf_test.crs = "EPSG:4326"
gdf_test = gdf_test.to_crs(gdf_tract.crs)

#%%
#plot shows that HHCImportType==1 is work order
fig = plt.figure()
ax = fig.add_subplot()
gdf_tract.plot(ax=ax, color='k')
gdf_test.loc[gdf_test.HHCImportType==9, :].plot(ax=ax, color='r')
#gdf_test.loc[gdf_test.HHCImportType==8, :].plot(ax=ax, color='b')
plt.show()

#%% 0: tree down, 1: limb down, 2: hanging limb
fig = plt.figure()
ax = fig.add_subplot(111)
gdf_tract.plot(ax=ax, color='k')
gdf_test.loc[gdf_test.Category==0, :].plot(ax=ax, color='r')
gdf_test.loc[gdf_test.Category==1, :].plot(ax=ax, color='orange')
gdf_test.loc[gdf_test.Category==2, :].plot(ax=ax, color='green')
plt.show()

#%% get list of events
path_Events = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\StormEvents.xlsx'
path_EventTypes =  r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\EventTypes.xlsx'
path_CriticalIssues =  r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\CriticalIssues.xlsx'
path_EventTypeCriticalIssues = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\EventTypeCriticalIssues.xlsx'
path_StormEventTypes = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\StormEventsTypes.xlsx'
df_Events = pd.read_excel(path_Events, parse_dates=['StartDate', 'EndDate'])
df_EventTypes = pd.read_excel(path_EventTypes)
df_CriticalIssues = pd.read_excel(path_CriticalIssues)
df_EventTypeCriticalIssues = pd.read_excel(path_EventTypeCriticalIssues)
df_StormEventTypes = pd.read_excel(path_StormEventTypes)

#%%  get hazard type id
type_name =  'Winter Storm'
type_id = df_EventTypes.loc[df_EventTypes.Name == type_name, 'Id'].values[0]

#%% get all storm events ids with this hazard type
df_EventIds = df_StormEventTypes.loc[df_StormEventTypes.EventTypeId==type_id,:]
df_EventIds.index = df_EventIds.StormEventId

#%% get storm events with this id after 2000
df_Events.index = df_Events.Id
df_Events = df_Events.loc[df_EventIds.index, :]
df_Events = df_Events.loc[df_Events.StartDate >= '2000-01-01', :]

#%% get tree service calls in this range
df_tree['Is_Event'] = np.zeros(len(df_tree))
for i, idx in enumerate(df_Events.index):
    start_date = df_Events.at[idx, 'StartDate']
    end_date = df_Events.at[idx, 'EndDate']
    df_tree.loc[ ( (df_tree.DateInitiated >= start_date) & (df_tree.DateInitiated <= end_date)), 'Is_Event'] = 1

#%%
df_tree = df_tree.loc[df_tree.Is_Event==1,:]

#%% only consider work orders
df_tree_2 = df_tree.loc[( (df_tree.HHCImportType !=0) & (df_tree.HHCImportType !=8)), :]

#%% assume all work orders are 3500
Loss_USD = len(df_tree_2) *3500 / 20


""" annual loss is ~ 100k.  Even if count all service requests still only ~1M.  
too small to include.  """



