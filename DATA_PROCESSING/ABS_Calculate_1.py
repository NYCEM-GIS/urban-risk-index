""" calculate absolute scores and percentiles for each hazard for total loss and total risk"""

#calculate all URI and ESL values

#%% read packages
import pandas as pd
import numpy as np
import geopandas as gpd
from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% open outputs path and get abbrev list
folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()
list_abbrev_haz.remove('CYB')

#%% open and stack all URI shapefiles
for i, haz in enumerate(list_abbrev_haz):
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format(haz, haz)
    gdf_this = gpd.read_file(path_haz)
    gdf_this['Haz'] = np.repeat(haz, len(gdf_this))
    #remove hazard name from column titles so they can be stacked
    gdf_this.columns = [x.replace(haz, '') for x in gdf_this.columns]
    if i==0:
        gdf_stack = gdf_this.copy()
    else:
        gdf_stack = gdf_stack.append(gdf_this)

#%% calculate score and percentile
gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='E_RNTT', score_column='E_RsTT')
gdf_stack = utils.calculate_percentile(gdf_stack, data_column='E_RNTT', score_column='E_RpTT')

gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='U_RN', score_column='U_Rs')
gdf_stack = utils.calculate_percentile(gdf_stack, data_column='U_RN', score_column='U_Rp')

#%% add absolute value to each URI shapefile
for i, haz in enumerate(list_abbrev_haz):
    path_uri = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format(haz)
    gdf_uri = gpd.read_file(path_haz)
    this_haz = gdf_stack.loc[gdf_stack['Haz']==haz].copy()[['BCT_txt', 'E_RsTT', 'E_RpTT', 'U_Rs', 'U_Rp']]
    this_haz.columns = [x.replace('E_', haz + 'E_') for x in this_haz.columns]
    this_haz.columns = [x.replace('U_', haz + 'U_') for x in this_haz.columns]
    gdf_uri = gdf_uri.merge(this_haz, on='BCT_txt', how='inner')
    gdf_uri.to_file(path_uri)
