""" calculate institutional experience based on county of events in HH&C"""

import numpy as np
import pandas as pd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import  PARAMS, ABBREVIATIONS
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_activation = PATHNAMES.RCA_RC_IE_activation
# Params
# This represents all the active hazards
list_abbrv = [x.abbreviation for x in ABBREVIATIONS.values() if (x.category == "Hazard") and  (x.status == 'Active')]
# Output paths
path_output = PATHNAMES.RCA_RC_IN_score

#%% LOAD DATA
df_activation = pd.read_excel(path_activation, sheet_name='Summary')
gdf_tract = utils.get_blank_tract()

#%% open EOC activation spreadsheet
print(df_activation.shape)

#%% Get list of hazards and EOC activation keyword
list_hazards = {'EXH': ['Heat'],
                'WIW': ['Winter Weather'], 
                'CSW': ['Coastal Storm'],  
                'CSF': ['Coastal Storm', 'Flooding']}

#%% Data preprocessing: Take only rows where CIMS TYPE is not na.
df_activation = df_activation[df_activation['CIMS TYPE'].notna()]

#%%
df_count = pd.DataFrame(index=np.arange(len(list_abbrv)),
                        data={'abbrv': list_abbrv,
                              'count_events': np.zeros(len(list_abbrv)),
                              'count_days': np.zeros(len(list_abbrv))})

#%% loop through each hazard to get count

for abbrev in list_hazards.keys():
    keyword_list = list_hazards[abbrev]
    df_activation[abbrev] = df_activation['CIMS TYPE'].str.contains('|'.join(keyword_list))
    subset = df_activation[df_activation[abbrev]].copy()
    df_count.loc[df_count.abbrv == abbrev, 'count_events'] = len(subset)
    df_count.loc[df_count.abbrv == abbrev, 'count_days'] = subset.DURATION.sum()


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
