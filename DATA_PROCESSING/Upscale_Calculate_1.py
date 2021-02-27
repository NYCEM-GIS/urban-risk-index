""" upscale results to calculate for NTA, PUMA, """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import plotting_1 as plotting
from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% open outputs path and get abbrev list and mitigation table
folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()

#%% loop through hazards and open
i=0
haz = list_abbrev_haz[i]

#%% open tract uri
path_uri = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format(haz)
gdf_uri = gpd.read_file(path_uri)

#%%



