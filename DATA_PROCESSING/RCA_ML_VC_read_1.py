""" get vegetative cover data"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% open vegetation dataset
path_veg = params.PATHNAMES.at['RCA_ML_VC_table', 'Value']
df_veg = pd.read_excel(path_veg)

#%%open neighborhood shapefile
epsg = params.SETTINGS.at['epsg', 'Value']
path_nta = params.PATHNAMES.at['BOUNDARY_neighborhood', 'Value']
gdf_nta = gpd.read_file(path_nta)
gdf_nta = gdf_nta.to_crs(epsg=epsg)

#%% join veg data gdf_nta
gdf_nta = gdf_nta.merge(df_veg, left_on='ntacode', right_on='NTA Code', how='left')

#%% fill in missing data with median value
gdf_nta.fillna(value={'Pct Veg Cover': gdf_nta['Pct Veg Cover'].median()}, inplace=True)

#%%open tract dataset
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = gdf_tract.to_crs(epsg=epsg)

#%% perform overlay and average
gdf_tract = utils.convert_to_tract_average(gdf_nta, column_name = 'Pct Veg Cover', column_name_out='Pct_Veg_Cover_Tract' )

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Pct_Veg_Cover_Tract', score_column='Score', n_cluster=5)

#%% save as output
path_output = params.PATHNAMES.at['RCA_ML_VC_score', 'Value']
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
print("Finished calculating RCA factor: Vegetative Cover.")
