""" calculates the combined RCA score based on the factors considered"""

#%% load packages
import geopandas as gpd
import os

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load the factors
# path_ac = params.PATHNAMES.at['RCA_EXT_AC', 'Value']
# gdf_ac = gpd.read_file(path_ac)

path_CC_CI = params.PATHNAMES.at['RCA_CC_CI_score', 'Value']
path_CC_EO = params.PATHNAMES.at['RCA_CC_EO_score', 'Value']
path_CC_PA = params.PATHNAMES.at['RCA_CC_PA_score', 'Value']
path_CC_PE = params.PATHNAMES.at['RCA_CC_PE_score', 'Value']

gdf_CI = gpd.read_file(path_CC_CI)
gdf_EO = gpd.read_file(path_CC_EO)
gdf_PA = gpd.read_file(path_CC_PA)
gdf_PE = gpd.read_file(path_CC_PE)

#%% run utility to combine the factors
list_factor_gdfs = [gdf_CI, gdf_EO, gdf_PA, gdf_PE]
list_factor_columns = ['Score', 'Score', 'Score', 'Score']
gdf_RCA = utils.calculate_RCA(list_factor_gdfs, list_factor_columns)

#%% save results in
path_results = params.PATHNAMES.at['EXH_RCA_composite_score', 'Value']
gdf_RCA.to_file(path_results)

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
print("Finished calculating EXH RCA composite score.")