""" get parks with green infrastructrure cover data"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load data
path_gi = params.PATHNAMES.at['RCA_ML_GI_raw', 'Value']
gdf_gi = gpd.read_file(path_gi)
gdf_gi = utils.project_gdf(gdf_gi)
gdf_gi['OBJECTID'] = np.arange(len(gdf_gi))

#%% load tracts
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

#%% crete buffered tracts
gdf_tract_buffer = gdf_tract.copy()
gdf_tract_buffer['geometry'] = gdf_tract['geometry'].buffer(distance = 528)
gdf_tract_buffer['area_buffer_mi2'] = gdf_tract_buffer['geometry'].area  / (5280*5280)

#%% get count in each tract
gdf_join = gpd.sjoin(gdf_tract_buffer, gdf_gi)
count = gdf_join['BCT_txt'].value_counts()
df_counts = pd.DataFrame(index=count.index, data={'count':count.values})

#%% join results to tracts
gdf_merge = gdf_tract.merge(df_counts, left_on='BCT_txt', right_index=True, how='left')
gdf_merge.fillna(value=0, inplace=True)
gdf_merge = utils.calculate_kmeans(gdf_merge, data_column='count', score_column='Score', n_cluster=5)

#%% save
path_output = params.PATHNAMES.at['RCA_ML_GI_score', 'Value']
gdf_merge.to_file(path_output)

plotting.plot_notebook(gdf_merge, column='Score', title='RCA_ML_GI: Green Infrastructure',
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
print("Finished calculating RCA factor: Green Infrastructure.")


