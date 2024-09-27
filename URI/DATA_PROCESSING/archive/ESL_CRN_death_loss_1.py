"""
calculate the total economic loss due to deaths from CRN
"""

#%% load packages
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Hard-coded values
value_loss_2016 = 81136410.00  # from spreadsheet
value_loss = utils.convert_USD(value_loss_2016, 2016)
# Output paths
path_results = PATHNAMES.ESL_CRN_death_loss

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)

#%%distribute by population
gdf_tract['Loss_USD'] = value_loss * gdf_tract['pop_2020'] / gdf_tract['pop_2020'].sum()

#%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CRN: Deaths Loss',
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
print("Finished calculating CRN loss due to deaths.")




