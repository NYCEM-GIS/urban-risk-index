""" power loww during coastal storms"""

import numpy as np
import pandas as pd
import os
import datetime
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting

utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_outages = params.PATHNAMES.at['ESL_CST_outages_data', 'Value']
# Params
outage_buffer  = params.PARAMS.at['buffer_period_power_outage_days', 'Value']
USD_per_hr_power_out = params.PARAMS.at['loss_day_power', 'Value'] / 24.
# Output paths
path_results = params.PATHNAMES.at['ESL_WIW_loss_power', 'Value']

#%% LOAD DATA
path_tree = r'\\surly.mcs.local\Projects\CCSI\TECH\2020_NYCURI\Working_Dano\1_RAW_INPUTS\OTH_HH_C\TreeServices.xlsx'
df_tree = pd.read_excel(path_tree, parse_dates=['DateInitiated', 'DateCreated'])
gdf_tract = utils.get_blank_tract()
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
df_outages = pd.read_excel(path_outages)

#%%  get hazard type id
type_name = 'Winter Storm'
type_id = df_EventTypes.loc[df_EventTypes.Name == type_name, 'Id'].values[0]

#%% get all storm events ids with this hazard type
df_EventsIds = df_Events.copy()
df_EventIds = df_StormEventTypes.loc[df_StormEventTypes.EventTypeId==type_id,:]
df_EventIds.index = df_EventIds.StormEventId

#%% get storm events with  over 10 year period
df_Events.index = df_Events.Id
df_Events = df_Events.loc[df_EventIds.index, :]
df_Events = df_Events.loc[df_Events.StartDate >= '2003-01-01', :]
df_Events = df_Events.loc[df_Events.StartDate < '2013-01-01', :]

#%% get power outages during these events
df_outages['Is_Event'] = np.zeros(len(df_outages))
for i, idx in enumerate(df_Events.index):
    start_date = df_Events.at[idx, 'StartDate']
    end_date = df_Events.at[idx, 'EndDate'] + datetime.timedelta(days=outage_buffer)
    df_outages.loc[ ( (df_outages.Timestamp >= start_date) & (df_outages.Timestamp <= end_date)), 'Is_Event'] = 1

#%% get outages
df_outages_1 = df_outages.loc[df_outages.Is_Event==1,:].copy()
df_outages_1.index = np.arange(len(df_outages_1))
df_outages_1['Duration_hr'] = np.zeros(len(df_outages_1))

#%% get duration of outages
list_DPSId = df_outages_1.DPSId.unique()
for i in np.arange(len(list_DPSId)):
    DPSId = list_DPSId[i]
    df_DPSId = df_outages_1.loc[df_outages_1.DPSId == DPSId].copy()
    df_DPSId = df_DPSId.sort_values(by='Timestamp')
    j_max = len(df_DPSId)
    for j, idx in enumerate(df_DPSId.index):
        if j < j_max-1:
            this_idx = idx
            next_idx = df_DPSId.index[j+1]
            this_time = df_DPSId.at[this_idx, 'Timestamp']
            next_time = df_DPSId.at[next_idx, 'Timestamp']
            try_duration = (next_time-this_time).total_seconds()/(60*60)
            if try_duration > 24:
                duration = np.nan
            else:
                duration  = try_duration
        else:
            duration = np.nan
        df_DPSId.at[idx, 'Duration_hr'] = duration
        #fill in nan values with median
        if df_DPSId['Duration_hr'].isna().sum() == len(df_DPSId):
            fill_na = 12.  #assume 12 hours if no better information
        else:
            fill_na = df_DPSId['Duration_hr'].median()
    df_DPSId.fillna(value=fill_na, inplace=True)
    df_outages_1.loc[df_DPSId.index, 'Duration_hr'] = df_DPSId['Duration_hr']

#%% sum lost hours, value, and aggregate to borough
df_outages_1['Person_hrs'] = df_outages_1['CustomersOut'] * df_outages_1['Duration_hr']
df_bor = df_outages_1[['Person_hrs', 'BoroughId']].groupby(by='BoroughId').sum()
df_bor['Loss_USD'] = USD_per_hr_power_out * df_bor['Person_hrs'] / (10.)  #multiply by 10 to annualize

#%% assign to borought
gdf_tract = utils.get_blank_tract(add_pop=True)
gdf_tract['Loss_USD'] = 0
for i, bor in enumerate(gdf_tract.BOROCODE.unique()):
    gdf_tract_bor = gdf_tract.loc[gdf_tract.BOROCODE==bor, :].copy()
    #assign losses by population
    gdf_tract_bor['Loss_USD'] = df_bor.at[int(bor), 'Loss_USD'] * gdf_tract_bor['pop_2010'] / gdf_tract_bor['pop_2010'].sum()
    gdf_tract.loc[gdf_tract_bor.index, 'Loss_USD'] = gdf_tract_bor['Loss_USD']

#%% #%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='WIW: Power Loss',
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
print("Finished calculating WIW loss due to power outage.")


