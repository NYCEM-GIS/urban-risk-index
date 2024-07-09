""" aggregate hazus losses, annualized coastal storms"""

#%% read packages
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
path_hazus = r".\1_RAW_INPUTS\CST_HAZUS\Coastal Storms Probabilistic Runs\100yr\100\results.shp"
# Output paths
path_output = PATHNAMES.ESL_CST_hazus_loss

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
df_hazus = gpd.read_file(path_hazus)

#%% convert from 2007 to URI dollars, multiply by 1000
df_hazus['Loss_USD'] = utils.convert_USD(df_hazus.EconLoss, 2007) * 1000.

#%% merge to tract
gdf_tract = gdf_tract.merge(df_hazus[['tract', 'Loss_USD']], left_on='geoid', right_on='tract', how='left')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CST: HAZUS Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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