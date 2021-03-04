""" read in the community infrastructure factor into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import scipy.stats as stats
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from census import Census
from us import states
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract()

#%% load place attachment data
c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8")
response_pop_older_1yr = c.acs5.state_county_tract('B07204_001E', states.NY.fips, '*', Census.ALL)
response_same_house_1yr_ago  = c.acs5.state_county_tract('B07204_002E', states.NY.fips, '*', Census.ALL)
response_diff_house_same_city_1yr_ago  = c.acs5.state_county_tract('B07204_005E', states.NY.fips, '*', Census.ALL)
list_tract1 = [x['tract'] for x in response_pop_older_1yr]
list_state = [x['state'] for x in response_pop_older_1yr]
list_county = [x['county'] for x in response_pop_older_1yr]
list_pop_older_1yr = [x['B07204_001E'] for x in response_pop_older_1yr]
list_tract2 = [x['tract'] for x in response_same_house_1yr_ago]
list_same_house_1yr_ago = [x['B07204_002E'] for x in response_same_house_1yr_ago]
list_tract3 = [x['tract'] for x in response_same_house_1yr_ago]
list_diff_house_same_city_1yr_ago = [x['B07204_005E'] for x in response_diff_house_same_city_1yr_ago]


#%%
df = pd.DataFrame(index=np.arange(len(list_tract1)), data={'pop_older_1yr':list_pop_older_1yr,
                                            'same_house_1yr_ago':list_same_house_1yr_ago,
                                            'diff_house_same_city_1yr_ago':list_diff_house_same_city_1yr_ago,
                                           'tract':list_tract1,
                                           'county':list_county,
                                           'state':list_state})
df['Stfid'] = [df.loc[x,"state"] + df.loc[x, 'county']+df.loc[x,'tract'] for x in df.index]

#%% merge
gdf_tract = gdf_tract.merge(df[['pop_older_1yr', 'Stfid', 'same_house_1yr_ago', 'diff_house_same_city_1yr_ago' ]], left_on='Stfid', right_on='Stfid', how='inner')

#%%
gdf_tract['percent_living_in_NY_over_1yr'] = (gdf_tract['same_house_1yr_ago'] + gdf_tract['diff_house_same_city_1yr_ago'])/gdf_tract['pop_older_1yr'] * 100.
#set missing values to median
gdf_tract.fillna(gdf_tract['percent_living_in_NY_over_1yr'].median() , inplace=True)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='percent_living_in_NY_over_1yr', n_cluster=5)


#%% save as output
path_output = params.PATHNAMES.at['RCA_CC_PA_score', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_CC_PA: Place Attachment',
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
print("Finished calculating RCA factor: Place attachment.")
