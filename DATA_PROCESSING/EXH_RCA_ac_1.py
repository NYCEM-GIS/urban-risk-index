"""
import ac data
convert into tract data with correct projection
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load AC data and convert to track average
path_ac = params.PATHNAMES.at['RCA_EXT_ac_raw', 'Value']
column_ac = "DATA_VALUE"
column_ac_out = "ac_per"

gdf_tract = utils.convert_to_tract_average(path_ac, column_ac,column_ac_out,
                               list_input_null_values=[-999], output_null_value=-999)

#%% calculate percent rank
gdf_tract['ac_per_rnk'] = utils.normalize_rank_percentile(gdf_tract['ac_per'].values,
                                                          list_input_null_values=[-999],
                                                          output_null_value=-999)

#%% save results in
path_results = params.PATHNAMES.at['RCA_EXT_AC', 'Value']
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

