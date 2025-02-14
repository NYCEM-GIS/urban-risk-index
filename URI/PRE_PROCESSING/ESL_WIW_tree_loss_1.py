import numpy as np
import pandas as pd
import geopandas as gpd
import os
import datetime
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_tree = PATHNAMES.HHC_TreeServices
path_Events = PATHNAMES.stormevents_table
path_EventTypes = PATHNAMES.HHC_eventtypes
path_StormEventTypes = PATHNAMES.HHC_stormeventtypes
# Params
service_buffer = HARDCODED.buffer_period_tree_servicing_days
# Output paths
path_results = PATHNAMES.ESL_WIW_loss_tree

#%% LOAD DATA
df_tree = pd.read_excel(path_tree, parse_dates=['DateInitiated', 'DateCreated'])
gdf_tract = utils.get_blank_tract()
df_Events = pd.read_excel(path_Events, parse_dates=['StartDate', 'EndDate'])
df_EventTypes = pd.read_excel(path_EventTypes)
df_StormEventTypes = pd.read_excel(path_StormEventTypes)

#%%  get hazard type id
type_name = 'Winter Weather'
type_id = df_EventTypes.loc[df_EventTypes.Name == type_name, 'Id'].values[0]

#%% get all storm events ids with this hazard type
df_EventsIds = df_Events.copy()
df_EventIds = df_StormEventTypes.loc[df_StormEventTypes.EventTypeId==type_id,:]
df_EventIds.index = df_EventIds.StormEventId

#%% get storm events with this id after 2000
df_Events.index = df_Events.Id
df_Events['StartDate'] = pd.to_datetime(df_Events['StartDate'])
df_Events['EndDate'] = pd.to_datetime(df_Events['EndDate'])
df_Events = df_Events.loc[df_EventIds.index, :]
df_Events = df_Events.loc[df_Events.StartDate >= datetime.datetime(year=2014, month=1, day=1), :]
df_Events = df_Events.loc[df_Events.EndDate < datetime.datetime(year=2024, month=1, day=1), :]

#%% get tree service calls in this range
df_tree['Is_Event'] = np.zeros(len(df_tree))
df_tree['DateInitiated'] = pd.to_datetime(df_tree['DateInitiated'])
for i, idx in enumerate(df_Events.index):
    start_date = df_Events.at[idx, 'StartDate']
    end_date = df_Events.at[idx, 'EndDate'] + datetime.timedelta(days=service_buffer)
    df_tree.loc[((df_tree.DateInitiated >= start_date) & (df_tree.DateInitiated <= end_date)), 'Is_Event'] = 1

#%%
df_tree_1 = df_tree.loc[df_tree.Is_Event == 1,:]

#%% only consider work orders
df_tree_2 = df_tree_1.loc[((df_tree_1.HHCImportType != 0) & (df_tree_1.HHCImportType != 8)), :]

#%% assume all work orders are 3500
Loss_USD = len(df_tree_2) * 3500 / 10

#%% plot distribution of tree services
gdf_tree = gpd.GeoDataFrame(df_tree_2, geometry=gpd.points_from_xy(df_tree_2.Long, df_tree_2.Lat))
gdf_tree = gdf_tree.loc[gdf_tree.Lat !=0, :]
gdf_tree = gdf_tree.loc[gdf_tree.Long !=0, :]
gdf_tree.crs = "EPSG:4326"
gdf_tree = utils.project_gdf(gdf_tree)

#%% get count per tract of tree services
gdf_join = gpd.sjoin(gdf_tree, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['Lat'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'Lat': 0}, inplace=True)
gdf_tract.rename(columns={"Lat":"Tree_Service_Count"}, inplace=True)

#%% distribute losses weighted by the Tree Seri
gdf_tract['Loss_USD'] = Loss_USD * gdf_tract['Tree_Service_Count'] / gdf_tract['Tree_Service_Count'].sum()

#%% #%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='WIW: Tree Servicing Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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
print("Finished calculating WIW loss due to tree servicing.")



