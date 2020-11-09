"""
get CDC SOVI score for each tract.
Normalize for NEW to scale between 0 and 100 using percent ranking


"""

#%%% import packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load cdc covi score at tract level and reproject
path_sovi = params.PATHNAMES.at['SOV_tract', 'Value']
gdf_sovi = gpd.read_file(path_sovi)
#reproject
epsg = params.SETTINGS.at['epsg', 'Value']
gdf_sovi = gdf_sovi.to_crs(epsg=epsg)

#%%load FIPS data
path_FIPS = params.PATHNAMES.at['Borough_to_FIP', 'Value']
df_FIPS = pd.read_excel(path_FIPS)

#%% load the census block and dissolve to census track
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False,
                                                        aggfunc='first')
gdf_tract['BoroCode_Int'] = [int(gdf_tract.at[x, 'BoroCode']) for x in gdf_tract.index]
gdf_tract = gdf_tract.merge(df_FIPS, left_on='BoroCode_Int', right_on='Bor_ID', how='inner')
gdf_tract['FIPS_CT'] = [str(gdf_tract.at[idx, 'FIPS']) + str(gdf_tract.at[idx, 'BCT_txt'])[1:] for idx in gdf_tract.index]
gdf_tract = gdf_tract.merge(gdf_sovi[['FIPS', 'RPL_THEMES']], left_on='FIPS_CT', right_on='FIPS', how='left')

#%% normalize result to scale of 0.01 to 0.99
gdf_tract['SOV_rank'] = utils.normalize_rank_percentile(gdf_tract['RPL_THEMES'].values,
                                                        list_input_null_values=[0, -999],
                                                        output_null_value=-999)

#%% save results in
path_results = params.PATHNAMES.at['SOV_results_raw', 'Value']
gdf_tract.to_file(path_results)

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_results)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating SOV score.")