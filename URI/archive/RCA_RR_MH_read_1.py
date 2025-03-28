""" median household income by tract"""

#%% read packages
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_cdc = PATHNAMES.SOV_tract
path_fips = PATHNAMES.Borough_to_FIP
# Output paths
path_output = PATHNAMES.RCA_RR_MH_score

#%% LOAD DATA
path_layer = os.path.basename(path_cdc)
path_gdb = os.path.dirname(path_cdc)
gdf_cdc = gpd.read_file(path_gdb, driver='FileGDB', layer=path_layer)
df_fips = pd.read_excel(path_fips)

#%% tract data
gdf_tract = utils.get_blank_tract()

#%% fips data
df_fips['Bor_ID_str'] = [str(df_fips.at[idx, 'Bor_ID']) for idx in df_fips.index]
df_fips['FIPS_mod'] = ['3600' + df_fips.at[idx, 'Bor_ID_str'] for idx in df_fips.index]

#add fips id number
gdf_tract = gdf_tract.merge(df_fips, left_on='borocode', right_on='Bor_ID_str', how='left')
gdf_tract['FIPS_CT_txt'] = [str(gdf_tract.at[idx, 'FIPS']) + gdf_tract.at[idx, 'BCT_txt'][1:] for idx in gdf_tract.index]

#%% merge displacement score
gdf_tract = gdf_tract.merge(gdf_cdc[['FIPS', 'E_POV150']], left_on='FIPS_CT_txt', right_on='FIPS', how='left')
#assign -999 values a value of 0
gdf_tract.loc[gdf_tract['E_POV150'] == -999, 'E_POV150'] = 0

#%% assign to value of 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='E_POV150')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_MH: Median Household Income',
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
print("Finished calculating RCA factor: median household income.")
