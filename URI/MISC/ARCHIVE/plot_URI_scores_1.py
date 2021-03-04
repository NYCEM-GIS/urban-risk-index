""" make plots for distribution, and notebooks"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests
from mpl_toolkits.axes_grid1 import make_axes_locatable

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%%
#%% get list of hazards
list_hazards = ['EXH', 'WIW', 'CST', 'CER', 'HIW', 'ERQ', 'FLD', 'EMG', 'RES', 'CRN', 'CYB']
list_names = ['Extreme Heat', 'Winter Weather', 'Coastal Storms', 'Coastal Erosion',
              'High Winds', 'Earthquake', 'Flooding', 'Emerging Disease', 'Respiratory Illness',
              'CBRN', 'Cyber Threats']

#%% get path to full URI shapefiles (produced by the notebooks).  open and create single shapefile with Stfid, haz, and URI_Raw
for i, haz in enumerate(list_hazards):
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
                haz, haz)
    gdf_haz = gpd.read_file(path_haz)
    name = list_names[i]
    fig = plt.figure(figsize=(13,6))
    plt.suptitle(name)
    list_col = ['URI_EI', 'URI', 'URI_QT']
    list_title = ['Equal Interval', 'K-means (Natural Breaks)', 'Quintiles']
    for j in np.arange(3):
        col = list_col[j]
        title = list_title[j]
        ax = fig.add_subplot(1,3,j+1)
        plt.axis('off')
        gdf_haz.plot(ax=ax, column=col, legend=True, cmap='Blues', categorical=True,
                      legend_kwds={'title': '{} {}'.format(haz, col), 'bbox_to_anchor': (.2, .9),
                                   'frameon': False})
        plt.title(title)
        gdf_haz.boundary.plot(ax=ax, color='k', lw=0.05)

    plt.tight_layout()
    plt.savefig(r'.\8_FIGURES\OTHER\SCORES\URI_Scores_{}_1.png'.format(haz), dpi=500)
    plt.show()

