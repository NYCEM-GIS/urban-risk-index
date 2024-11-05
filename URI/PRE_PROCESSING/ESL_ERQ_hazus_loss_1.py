""" incorporate flooding damaage due to coastal storms"""

#%% read packages
import geopandas as gpd
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()
#%% EXTRACT PARAMETERS
# Input paths
path_erq_hazus = PATHNAMES.ESL_ERQ_hazus
# Output paths
path_output = PATHNAMES.ESL_ERQ_hazus_loss

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)
df_hazus = gpd.read_file(path_erq_hazus)

#%% use tract to merge hazus data to tract
gdf_tract = gdf_tract.merge(df_hazus[['tract', 'EconLoss']], left_on='geoid', right_on='tract', how='left')

#%% convert to current USD
gdf_tract.EconLoss = utils.convert_USD(gdf_tract.EconLoss.values, 2018)

#%% total loss is in USD 1000.... convert
gdf_tract['Loss_USD'] = gdf_tract['EconLoss'] * 1000.

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='ERQ: Building Damage',
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
print("Finished calculating ERQ Building Damage.")