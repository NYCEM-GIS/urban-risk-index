""" calculate institutional experience based on county of events in HH&C"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%%% open tract
gdf_tract = utils.get_blank_tract()

#%% open EOC activation spreadsheet
path_activation = params.PATHNAMES.at['RCA_RC_IE_activation', 'Value']
df_activation = pd.read_excel(path_activation)
df_activation = pd.read_excel('.\\1_RAW_INPUTS\\OTH_HH_C\\EOCActivations_test_Shweta.xlsx')
print(df_activation.shape)

#%% Get list of hazards and EOC activation keyword
list_hazards = ( ('EXH', 'Heat'),
                 ('WIW', 'Winter Weather'),     #Winter Storm, na
                 ('CST', 'Coastal Storm'),     #Coastal Storm, na
                 ('FLD', 'Flooding'))  #Coastal Erosion, na

list_abbrv = params.ABBREVIATIONS.iloc[0:11, 0].values

#%%
df_count = pd.DataFrame(index=np.arange(len(list_abbrv)), data={'abbrv': list_abbrv,
                                                                'count_events':np.zeros(len(list_abbrv)),
                                                                'count_days':np.zeros(len(list_abbrv))})

#%% loop through each hazard to get count
for i in np.arange(len(list_hazards)):
    abbrev = list_hazards[i][0]
    name = list_hazards[i][1]
    bool = [name in x for x in df_activation.loc[:, 'Hazard']]
    this_activation = df_activation.loc[bool,:]
    df_count.loc[df_count.abbrv==abbrev, 'count_events'] = len(this_activation)
    df_count.loc[df_count.abbrv == abbrev, 'count_days'] = this_activation.Duration.sum()

## Legacy Code
# #%% get event data
# path_StormEvents = params.PATHNAMES.at['stormevents_table', 'Value']
# path_StormEventTypes = params.PATHNAMES.at['HHC_stormeventtypes', 'Value']
# path_StormEventIssues = params.PATHNAMES.at['HHC_storm_event_issues', 'Value']
# path_EventTypes = params.PATHNAMES.at['HHC_eventtypes', 'Value']
# path_CriticalIssues = params.PATHNAMES.at['HHC_critical_issues', 'Value']
#
# df_storm_events = pd.read_excel(path_StormEvents)
# df_storm_event_types = pd.read_excel(path_StormEventTypes)
# df_storm_event_issues = pd.read_excel(path_StormEventIssues)
# df_event_types = pd.read_excel(path_EventTypes)
# df_critical_issues = pd.read_excel(path_CriticalIssues)
#
# #%% get all storm events from 1999 to 2019
# df_storm_events = df_storm_events.loc[df_storm_events.StartDate >= '1999-01-01', :]
# df_storm_events = df_storm_events.loc[df_storm_events.StartDate < '2020-01-01', :]
#
# #%% describe criteria for each hazard as (hazard abbrev., event_id, issue_id), ...)
# #a zero means do not consider.  E.g., for WIW, only look at event id
# list_hazards = ( ('EXH', 1, 6),     #Extreme Temperatures, Extreme Heat
#                  ('WIW', 2, 0),     #Winter Storm, na
#                  ('CST', 6, 0),     #Coastal Storm, na
#                  ('CER', 7, 0),     #Coastal Erosion, na
#                  ('CYB', 11, 0),    #Cyber Threat, na
#                  ('RES', 0, 37),     #na, Pandemic
#                  ('EMG', 0, 32),     #na, Epidemic
#                  ('CRN', 10, 0),    #CBRNE, na
#                  ('HIW', 0, 13),     #na, High Winds
#                  ('ERQ', 8, 0),     #Earthquake, na
#                  ('FLD', 4, 0) )    #Flooding, na
#
#
# #%% get event count
# list_abbrv = [list_hazards[i][0] for i in np.arange(len(list_hazards))]
# df_count = pd.DataFrame(index=np.arange(len(list_abbrv)), data={'abbrv': list_abbrv,
#                                                                 'count_events':np.zeros(len(list_abbrv)),
#                                                                 'count_issues':np.zeros(len(list_abbrv)),
#                                                                 'count_total':np.zeros(len(list_abbrv))})
# #loop thorugh each hazard to get a count
# for idx in df_count.index:
#     this_abbrv = list_hazards[idx][0]
#     this_event_id = list_hazards[idx][1]
#     this_issued_id =  list_hazards[idx][2]
#     #get storm events of this hazard type
#     this_storm_events = df_storm_events.copy()
#     #check if the event id matches
#     this_storm_events['Matches_event'] = 0   #define bool if event is hazard type, assume not (=0)
#     if this_event_id == 0:
#         this_storm_events['Matches_event']  = 1
#     else:
#         #loop through each event id
#         for i, idx_events in enumerate(this_storm_events.index):
#             this_id = this_storm_events.at[idx_events, 'Id']
#             #get all event types for this id
#             this_list_event_ids =df_storm_event_types.loc[df_storm_event_types.StormEventId==this_id, 'EventTypeId'].values
#             if this_event_id in this_list_event_ids:
#                 this_storm_events.at[idx_events, 'Matches_event'] = 1
#
#     #check if the issue id matches
#     this_storm_events['Matches_issue'] = 0   #define bool if event is hazard type, assume not (=0)
#     if this_issued_id == 0:
#         this_storm_events['Matches_issue'] = 1
#     else:
#         #loop through each event id
#         for i, idx_events in enumerate(this_storm_events.index):
#             this_id = this_storm_events.at[idx_events, 'Id']
#             #get all issue types for this id
#             this_list_issue_ids =df_storm_event_issues.loc[df_storm_event_issues.StormEventId==this_id, 'CriticalIssueId'].values
#             if this_issued_id in this_list_issue_ids:
#                 this_storm_events.at[idx_events, 'Matches_issue'] = 1
#
#     def match_both(x, y):
#         if x==1:
#             if y==1:
#                 return 1
#         else:
#             return 0
#     this_storm_events['Matches_both'] = this_storm_events.apply(lambda row : match_both(row['Matches_event'],
#                                                                                          row['Matches_issue']),
#                                                                                           axis=1)
#     df_count.at[idx, 'count_events'] = this_storm_events.Matches_event.sum()
#     df_count.at[idx, 'count_issues'] = this_storm_events.Matches_issue.sum()
#     df_count.at[idx, 'count_total'] = this_storm_events.Matches_both.sum()

#%% calculate k-means cluster score
df_count = utils.calculate_kmeans(df_count, 'count_days')

#%% add results as score
for abbrv in list_abbrv:
    gdf_tract['Score_{}'.format(abbrv)] = np.repeat(df_count.loc[df_count.abbrv==abbrv, 'Score'].values[0], len(gdf_tract))
    gdf_tract['EOC_Duration_days_{}'.format(abbrv)] = np.repeat(df_count.loc[df_count.abbrv == abbrv, 'count_days'].values[0],
                                                    len(gdf_tract))

#%% save as output
path_output = params.PATHNAMES.at['RCA_RC_IN_score', 'Value']
gdf_tract.to_file(path_output)


#%% plot
for haz in list_abbrv:
    plotting.plot_notebook(gdf_tract, column='Score_'+haz, title='RCA_RC_IN: Institutional Experience ({})'.format(haz),
                           legend='Score', cmap='Blues', type='score')

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
print("Finished calculating RCA factor: Institutional Experience.")
