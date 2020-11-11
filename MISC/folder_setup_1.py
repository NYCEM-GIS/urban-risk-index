""" set up folder structures"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% make output folder for each hazard
list_abbrev = params.ABBREVIATIONS.iloc[0:11, 0].values
for abbrev in list_abbrev:
    path_dir = './3_OUTPUTS/{}'.format(abbrev)
    os.mkdir(path_dir)