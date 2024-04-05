""" health coverage by tract"""

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
path_cdc = params.PATHNAMES.at['RCA_MHI_cdc_sov', 'Value']
path_block = params.PATHNAMES.at['census_blocks', 'Value']
path_fips = params.PATHNAMES.at['Borough_to_FIP', 'Value']
# Settings
epsg = params.SETTINGS.at['epsg', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_RR_HI_score', 'Value']

#%% LOAD DATA
gdf_cdc = gpd.read_file(path_cdc)
gdf_block = gpd.read_file(path_block)
df_fips = pd.read_excel(path_fips)

#%% modify tract data
gdf_tract = gdf_block[['BCT_txt', 'borocode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = gdf_tract.to_crs(epsg=epsg)

#%% modify fips data
df_fips['Bor_ID_str'] = [str(df_fips.at[idx, 'Bor_ID']) for idx in df_fips.index]
df_fips['FIPS_mod'] = ['3600' + df_fips.at[idx, 'Bor_ID_str'] for idx in df_fips.index]

#add fips id number
gdf_tract = gdf_tract.merge(df_fips, left_on='borocode', right_on='Bor_ID_str', how='left')
gdf_tract['FIPS_CT_txt'] = [str(gdf_tract.at[idx, 'FIPS']) + gdf_tract.at[idx, 'BCT_txt'][1:] for idx in gdf_tract.index]

#%% merge displacement score
gdf_tract = gdf_tract.merge(gdf_cdc[['FIPS', 'EP_UNINSUR']], left_on='FIPS_CT_txt', right_on='FIPS', how='left')
#assign -999 values a value of 0
gdf_tract.loc[gdf_tract['EP_UNINSUR']==-999, 'EP_UNINSUR'] = np.median(gdf_tract['EP_UNINSUR'])

#%% assign to value of 1-5
gdf_tract['EP_Insure'] = 100. - gdf_tract['EP_UNINSUR']
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='EP_Insure')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_HI: Health Insurance Coverage',
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
print("Finished calculating RCA factor: health insurance coverage.")
