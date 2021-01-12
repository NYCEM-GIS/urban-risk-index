"""
calculate the total economic loss due to deeaths from CRN
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% load gdf_tracts
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% convert value of lost life to 2019 value
value_loss_2019 = 6.639662 * 1000000   #from spreadsheet
value_loss = utils.convert_USD(value_loss_2019, 2019)

#%%distribute by population
gdf_tract['Loss_USD'] = value_loss / len(gdf_tract)


#%% save results in
path_results = params.PATHNAMES.at['ESL_CYB_econ_loss', 'Value']
gdf_tract.to_file(path_results)

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




