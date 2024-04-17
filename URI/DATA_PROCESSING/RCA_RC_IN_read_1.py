""" calculate institutional experience based on county of events in HH&C"""

import numpy as np
import pandas as pd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_activation = params.PATHNAMES.at['RCA_RC_IE_activation', 'Value']
# Params
# This represents all the hazard abbreviations, excluding SOV, RCA, ESL, and OTH
list_abbrv = params.ABBREVIATIONS.iloc[0:11, 0].values
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_IN_score', 'Value']

#%% LOAD DATA
df_activation = pd.read_excel(path_activation, sheet_name='Summary')
gdf_tract = utils.get_blank_tract()

#%% open EOC activation spreadsheet
print(df_activation.shape)

#%% Get list of hazards and EOC activation keyword
list_hazards = (('EXH', 'Heat'),
                ('WIW', 'Winter Weather'),  # Winter Storm, na
                ('CST', 'Coastal Storm'),  # Coastal Storm, na
                ('FLD', 'Flooding'))  # Coastal Erosion, na


#%%
df_count = pd.DataFrame(index=np.arange(len(list_abbrv)),
                        data={'abbrv': list_abbrv,
                              'count_events': np.zeros(len(list_abbrv)),
                              'count_days': np.zeros(len(list_abbrv))})

#%% loop through each hazard to get count
for i in np.arange(len(list_hazards)):
    abbrev = list_hazards[i][0]
    name = list_hazards[i][1]
    bool = [name in x for x in df_activation.loc[:, 'CIMS TYPE']]
    this_activation = df_activation.loc[bool, :]
    df_count.loc[df_count.abbrv == abbrev, 'count_events'] = len(this_activation)
    df_count.loc[df_count.abbrv == abbrev, 'count_days'] = this_activation.DURATION.sum()


#%% calculate k-means cluster score
df_count = utils.calculate_kmeans(df_count, 'count_days')

#%% add results as score
for abbrv in list_abbrv:
    gdf_tract['Score_{}'.format(abbrv)] = np.repeat(df_count.loc[df_count.abbrv == abbrv, 'Score'].values[0], len(gdf_tract))

#%% save as output
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
