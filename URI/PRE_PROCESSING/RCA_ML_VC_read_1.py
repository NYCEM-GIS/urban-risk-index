""" get vegetative cover data"""

#%% read packages
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_veg = PATHNAMES.RCA_ML_VC_table
path_nta = PATHNAMES.BOUNDARY_neighborhood
# Output paths
path_output = PATHNAMES.RCA_ML_VC_score

#%% LOAD DATA
df_veg = pd.read_excel(path_veg)
gdf_tract = utils.get_blank_tract()

#%% Join vegetative data to tracts
df_veg['geoid'] = df_veg['geoid'].astype(str)
gdf_tract = gdf_tract.merge(df_veg, left_on='geoid', right_on='geoid', how='left')

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Pct_Veg_Cover_Tract', score_column='Score', n_cluster=5)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_ML_VC: Vegetative Cover',
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
print("Finished calculating RCA factor: Vegetative Cover.")
