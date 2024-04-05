""" get parks with water features cover data"""

#%% read packages
import numpy as np
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_pwf = params.PATHNAMES.at['RCA_ML_PWF_raw', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_ML_PW_score', 'Value']

#%% LOAD DATA
gdf_pwf = gpd.read_file(path_pwf)

#%% modify 
gdf_pwf = utils.project_gdf(gdf_pwf)
gdf_pwf['OBJECTID'] = np.arange(len(gdf_pwf))

#%% calculate radial count, 1/2 mile
gdf_tract = utils.calculate_radial_count(gdf_pwf, column_key= 'OBJECTID', buffer_distance_ft=2640)

#%% xconvert to score 1-5
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Fraction_Covered', score_column='Score', n_cluster=5)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_ML_PW: Parks with Water Feature',
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
print("Finished calculating RCA factor: parks with water feature.")