"""
calculate the total economic loss due to deeaths from CRN
"""

#%% load packages
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Output paths
path_results = PATHNAMES.ESL_CYB_econ_loss
# Hard-coded
value_loss_2019 = 663.966 * 1000000   #from spreadsheet
value_loss = utils.convert_USD(value_loss_2019, 2019)

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)

#%%distribute by population
gdf_tract['Loss_USD'] = value_loss / len(gdf_tract)

#%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CYB: Economic Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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
print("Finished calculating CYB loss due to economic losses.")




