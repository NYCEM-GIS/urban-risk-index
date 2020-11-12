""" aggregatet hazus losses, annualized coastal storms"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

# %% open tract
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

#%% open hazus data
path_gdb = params.PATHNAMES.at['ESL_CST_hazus', 'Value']
gdf_hazus = gpd.read_file(path_gdb, driver='FileGDB', layer='HAZUS_Hurricane_Annualized_Loss')
gdf_hazus.index = np.arange(len(gdf_hazus))
gdf_hazus = utils.project_gdf(gdf_hazus)

#%% open FIPS code
path_fips = params.PATHNAMES.at['Borough_to_FIP', 'Value']
df_fips = pd.read_excel(path_fips)

#%% create BCT_txt index in the hazus dataset
gdf_hazus['fips'] = [gdf_hazus.at[idx, 'tract'][0:5] for idx in gdf_hazus.index]
gdf_hazus['borocode'] = [df_fips.loc[df_fips['FIPS']==int(gdf_hazus.at[idx, 'fips']), 'Bor_ID'].values[0] for idx in gdf_hazus.index]
gdf_hazus['BCT_txt'] = [str(gdf_hazus.at[idx, 'borocode']) + str(gdf_hazus.at[idx, 'tract'][5:]) for idx in gdf_hazus.index]

#%% merge costs to tract
gdf_tract = gdf_tract.merge(gdf_hazus[['BCT_txt', 'Total']], on='BCT_txt', how='left')
gdf_tract['Loss_USD'] = gdf_tract['Total'] * 1000.0 #assume 1000 per

#drop nan values and set to 0, for now
gdf_tract.fillna(value={'Loss_USD':0}, inplace=True)

#%% save as output
path_output = params.PATHNAMES.at['ESL_CST_hazus_loss', 'Value']
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
print("Finished calculating CST Hazus loss.")