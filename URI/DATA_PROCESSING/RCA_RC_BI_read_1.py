""" get bikability score"""

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
path_bikescore = params.PATHNAMES.at['RCA_RC_BI_bikescore_csv', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_RC_BI_score', 'Value']

#%% LOAD DATA
df_bikescore  = pd.read_csv(path_bikescore)

#%% load tracts a
gdf_tract = utils.get_blank_tract()
gdf_tract.index = np.arange(len(gdf_tract))

gdf_tract_wgs = gdf_tract.to_crs(epsg=4326)
gdf_tract['lat'] = gdf_tract_wgs.geometry.centroid.y
gdf_tract['lon'] = gdf_tract_wgs.geometry.centroid.x


#%% load walkscore and merge to tract shapefile
temp = df_bikescore['BCT_txt']
df_bikescore['BCT_txt'] = [str(x) for x in temp]
gdf_tract = gdf_tract.merge(df_bikescore[['BCT_txt', 'bikescore']], on='BCT_txt', how='left')

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='bikescore')

#%% save as output
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
print("Finished calculating RCA factor: bikability.")

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_BI: Bikability',
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