""" calculates the combined RCA score based on the factors considered"""

#%% load packages
import geopandas as gpd
import os

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load the factors
path_ac = params.PATHNAMES.at['RCA_EXT_AC', 'Value']
gdf_ac = gpd.read_file(path_ac)

#%% run utility to combine the factors
list_factor_gdfs = [gdf_ac]
list_factor_columns = ['ac_per_rnk']
gdf_RCA = utils.calculate_RCA(list_factor_gdfs, list_factor_columns)

#%% save results in
path_results = params.PATHNAMES.at['EXH_RCA_composite_score', 'Value']
gdf_RCA.to_file(path_results)

#%%  document result with readme
text = """ 
The data was produced by {}
Located in {}
""".format(os.path.basename(__file__), os.path.dirname(__file__))
path_readme = os.path.dirname(path_results)
utils.write_readme(path_readme, text)

#%% output complete message
print("Finished calculating EXH RCA composite score.")