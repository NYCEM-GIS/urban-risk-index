""" read in the political engagement map into tract level map"""

#Missing Census tract number in data

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_data = params.PATHNAMES.at['RCA_CC_PE_data', 'Value']
path_block = params.PATHNAMES.at['census_blocks', 'Value']
path_fips = params.PATHNAMES.at['Borough_to_FIP', 'Value']
# Settings
epsg = params.SETTINGS.at['epsg', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_CC_PE_score', 'Value']

#%% LOAD DATA
df_data = pd.read_excel(path_data)
gdf_block = gpd.read_file(path_block)
df_fips = pd.read_excel(path_fips)

#%% place attachment data
df_data.dropna(inplace=True, subset=['Census Tract', 'Avg. Participation Score 2018']) #due to missing census tract number in data
df_data['FIPS_CT_txt'] = [str(int(df_data.at[idx, 'Census Tract'])) for idx in df_data.index]

#%% tract data
gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = gdf_tract.to_crs(epsg=epsg)

#%% fips data
df_fips['Bor_ID_str'] = [str(df_fips.at[idx, 'Bor_ID']) for idx in df_fips.index]
df_fips['FIPS_mod'] = ['3600' + df_fips.at[idx, 'Bor_ID_str'] for idx in df_fips.index]

#add fips id number
gdf_tract = gdf_tract.merge(df_fips, left_on='borocode', right_on='Bor_ID_str', how='left')
gdf_tract['FIPS_CT_txt'] = [str(gdf_tract.at[idx, 'FIPS_mod']) + gdf_tract.at[idx, 'BCT_txt'][1:] for idx in gdf_tract.index]

#%% merge displacement score
gdf_tract = gdf_tract.merge(df_data[['FIPS_CT_txt', 'Avg. Participation Score 2018']], left_on='FIPS_CT_txt', right_on='FIPS_CT_txt', how='left')

#%% fill na value with median voter participation score
values = {'Avg. Participation Score 2018':gdf_tract['Avg. Participation Score 2018'].median()}
gdf_tract.fillna(value=values, inplace=True)

#%% reclassify to score 1-5
gdf_tract['Score'] = np.zeros(len(gdf_tract))
for i, idx in enumerate(gdf_tract.index):
    this_value = gdf_tract.at[idx, 'Avg. Participation Score 2018']
    if this_value <= 21.8:
        this_score = 1
    elif this_value <= 26.8:
        this_score = 2
    elif this_value <= 31.6:
        this_score = 3
    elif this_value <= 37.9:
        this_score = 4
    else:
        this_score = 5
    gdf_tract.at[idx, 'Score'] = this_score

#%% save as output
gdf_tract.to_file(path_output)

plotting.plot_notebook(gdf_tract, column='Score', title='RCA_CC_PE: Political Engagement',
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
print("Finished calculating RCA factor: Political engagement.")
