import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests
import datetime
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting

utils.set_home()

#%% load gree service data
path_tree = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\TreeServices.xlsx'
df_tree = pd.read_excel(path_tree, parse_dates=['DateInitiated', 'DateCreated'])

#%%% visualize the results
gdf_tract = utils.get_blank_tract()

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
type_name = 'Winter Storm'
type_id = df_EventTypes.loc[df_EventTypes.Name == type_name, 'Id'].values[0]

#%% get all storm events ids with this hazard type
df_EventsIds = df_Events.copy()
df_EventIds = df_StormEventTypes.loc[df_StormEventTypes.EventTypeId==type_id,:]
df_EventIds.index = df_EventIds.StormEventId

#%% get storm events with this id after 2000
df_Events.index = df_Events.Id
df_Events = df_Events.loc[df_EventIds.index, :]
df_Events = df_Events.loc[df_Events.StartDate >= '2009-01-01', :]
df_Events = df_Events.loc[df_Events.StartDate < '2019-01-01', :]

#%% get tree service calls in this range
df_tree['Is_Event'] = np.zeros(len(df_tree))
for i, idx in enumerate(df_Events.index):
    start_date = df_Events.at[idx, 'StartDate']
    end_date = df_Events.at[idx, 'EndDate'] + datetime.timedelta(days=2)
    df_tree.loc[ ( (df_tree.DateInitiated >= start_date) & (df_tree.DateInitiated <= end_date)), 'Is_Event'] = 1

#%%
df_tree_1 = df_tree.loc[df_tree.Is_Event==1,:]

#%% only consider work orders
df_tree_2 = df_tree_1.loc[( (df_tree_1.HHCImportType !=0) & (df_tree_1.HHCImportType !=8)), :]

#%% assume all work orders are 3500
Loss_USD = len(df_tree_2) *3500 / 10

#%% plot distribution of tree services
gdf_tree = gpd.GeoDataFrame(df_tree, geometry=gpd.points_from_xy(df_tree.Long, df_tree.Lat))
gdf_tree = gdf_tree.loc[gdf_tree.Lat !=0, :]
gdf_tree = gdf_tree.loc[gdf_tree.Long !=0, :]
gdf_tree.crs = "EPSG:4326"
gdf_tree = gdf_tree.to_crs(gdf_tract.crs)

#%% get count per tract of tree services
gdf_join = gpd.sjoin(gdf_tree, gdf_tract, how='left', op='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['Lat'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'Lat': 0}, inplace=True)
gdf_tract.rename(columns={"Lat":"Tree_Service_Count"}, inplace=True)

#%% distribute losses weighted by the Tree Seri
gdf_tract['Loss_USD'] = Loss_USD * gdf_tract['Tree_Service_Count'] / gdf_tract['Tree_Service_Count'].sum()

#%% #%% save results in
path_results = params.PATHNAMES.at['ESL_WIW_loss_tree', 'Value']
gdf_tract.to_file(path_results)

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
print("Finished calculating CST loss due to tree servicing.")



