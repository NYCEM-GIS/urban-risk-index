""" read in the community infrastructure factor into tract level map"""
#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
from sklearn.cluster import KMeans
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_data = params.PATHNAMES.at['RCA_CC_community_infrastructure_raw', 'Value']
path_block = params.PATHNAMES.at['census_blocks', 'Value']
path_tract = params.PATHNAMES.at['boundary_tract', 'Value']
# Settings
epsg = params.SETTINGS.at['epsg', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_CC_CI_score', 'Value']

#%% LOAD DATA
gdf_data = gpd.read_file(path_data)  # community centers
gdf_block = gpd.read_file(path_block)

#%% tract data
gdf_data = gdf_data.to_crs(epsg=epsg)
gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = gdf_tract.to_crs(epsg=epsg)
gdf_tract['area_ft2'] = gdf_tract['geometry'].area
gdf_tract.to_file(path_tract)

#%% make shapefile with 1/2 mile radius
gdf_buffer = gdf_data.copy()
gdf_buffer['geometry'] = gdf_data['geometry'].buffer(distance=5280/2)

#%% create empty df to fill
df_fill = pd.DataFrame(columns=['BCT_txt', 'Fraction_Covered'])

#%% loop through each buffer, and add BCT_txt and area filled to list
for i, idx in enumerate(gdf_buffer.index):
    this_buffer = gdf_buffer.loc[[idx]]
    # take intersection
    this_intersect = gpd.overlay(gdf_tract, this_buffer[['OBJECTID', 'geometry']], how='intersection')
    this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
    this_intersect['Fraction_Covered'] = np.minimum(this_intersect['area_intersect_ft2'] / this_intersect['area_ft2'], 1.0)
    # add to df_fill
    df_fill = df_fill.append(this_intersect[['BCT_txt', 'Fraction_Covered']])

#%% get the sum  by tract and join
df_sum = df_fill.groupby(by='BCT_txt').sum()
gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')

# fill nan with value 0
gdf_tract.fillna(0, inplace=True)

# cluter to score by 5
kmeans = KMeans(n_clusters=5)
gdf_tract['Cluster_ID'] = kmeans.fit_predict(gdf_tract[['Fraction_Covered']])

#%% make lookup for class label
df_label = pd.DataFrame()
df_label['Cluster_ID'] = np.arange(5)
df_label['Cluster_Center'] = kmeans.cluster_centers_.flatten()
df_label.sort_values('Cluster_Center', inplace=True)
df_label['Label'] = ['Low', 'Med-Low', 'Med', 'Med-High', 'High']
df_label['Score'] = np.arange(1, 6)

# assign score to each cluster
gdf_tract = gdf_tract.merge(df_label[['Cluster_ID', 'Score']], on='Cluster_ID', how='left')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_CC_CI: Community Infrastructure',
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
print("Finished calculating RCA factor: Community Infrastructure.")
