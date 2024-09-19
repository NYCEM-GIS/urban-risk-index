""" read in the Income Equality (Gini index) into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import os
from census import Census
from us import states
import requests
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Output paths
path_output = PATHNAMES.RCA_RR_IE_score

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
session = requests.Session()
session.verify = False
c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8", session=session)

#%% place attachment data
gini_val = c.acs5.state_county_tract('B19083_001E', states.NY.fips, '*', Census.ALL)

#%%
list_tract1 = [x['tract'] for x in gini_val]
list_state = [x['state'] for x in gini_val]
list_county = [x['county'] for x in gini_val]
list_gini = [x['B19083_001E'] for x in gini_val]

#%%
df = pd.DataFrame(index=np.arange(len(list_tract1)), data={'gini':list_gini,
                                           'tract':list_tract1,
                                           'county':list_county,
                                           'state':list_state})
df['Stfid'] = [df.loc[x, "state"] + df.loc[x, 'county']+df.loc[x, 'tract'] for x in df.index]
#%% merge
gdf_tract = gdf_tract.merge(df[['gini', 'Stfid']], left_on='geoid', right_on='Stfid', how='inner')

#%%
gdf_tract.fillna(0, inplace=True)


#%%na values are -666666666.... set to median gini values for now
def adjust_nan(val):
    if val == -666666666.0:
        result = gdf_tract['gini'].median()
    else:
        result = val
    return result


gdf_tract['gini_adj'] = gdf_tract.apply(lambda row: adjust_nan(row['gini']), axis=1)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='gini_adj', score_column='Score', n_cluster=5, reverse=True)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_IE: Income Inequality',
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
print("Finished calculating RCA factor: Income inequality.")
