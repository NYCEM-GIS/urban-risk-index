""" read in the home ownership factor into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import os
from census import Census
from us import states
import requests
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Output paths
path_output = PATHNAMES.RCA_RR_HO_score

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
session = requests.Session()
session.verify = False
c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8", session=session)

#%% place attachment data
response_total = c.acs5.state_county_tract('B25026_001E', states.NY.fips, '*', Census.ALL)
response_owners = c.acs5.state_county_tract('B25026_002E', states.NY.fips, '*', Census.ALL)
list_tract1 = [x['tract'] for x in response_total]
list_state = [x['state'] for x in response_total]
list_county = [x['county'] for x in response_total]
list_total = [x['B25026_001E'] for x in response_total]
list_tract2 = [x['tract'] for x in response_owners]
list_owner = [x['B25026_002E'] for x in response_owners]

#%%
df = pd.DataFrame(index=np.arange(len(list_tract1)),
                  data={'owner': list_owner,
                        'tot': list_total,
                        'tract': list_tract1,
                        'county': list_county,
                        'state': list_state})
df['Stfid'] = [df.loc[x, "state"] + df.loc[x, 'county']+df.loc[x, 'tract'] for x in df.index]

#%% merge
gdf_tract = gdf_tract.merge(df[['owner', 'Stfid', 'tot']], left_on='geoid', right_on='Stfid', how='inner')

#%%
gdf_tract['percent_home_owner'] = gdf_tract['owner']/gdf_tract['tot'] * 100.
gdf_tract.fillna(0, inplace=True)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='percent_home_owner', score_column='Score', n_cluster=5)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_HO: Home Ownership',
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
print("Finished calculating RCA factor: Home ownership.")
