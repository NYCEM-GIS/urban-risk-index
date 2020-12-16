""" read in the community infrastructure factor into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from census import Census
from us import states
from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract()

#%% load place attachment data
c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8")
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
df['Stfid'] = [df.loc[x,"state"] + df.loc[x, 'county']+df.loc[x,'tract'] for x in df.index]
#%% merge
gdf_tract = gdf_tract.merge(df[['gini', 'Stfid']], left_on='Stfid', right_on='Stfid', how='inner')

#%%
gdf_tract.fillna(0, inplace=True)

#%%na values are -666666666.... set to median gini values for now
def adjust_nan(val):
    if val==-666666666.0:
        result = gdf_tract['gini'].median()
    else:
        result= val
    return result
gdf_tract['gini_adj'] = gdf_tract.apply(lambda row: adjust_nan(row['gini']), axis=1)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='gini_adj', score_column='Score', n_cluster=5)

#%% save as output
path_output = params.PATHNAMES.at['RCA_RR_IE_score', 'Value']
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
print("Finished calculating RCA factor: Gini Coefficient.")
