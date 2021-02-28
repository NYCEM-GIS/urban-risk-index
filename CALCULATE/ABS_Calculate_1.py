""" calculate absolute scores and percentiles for each hazard for total loss and total risk"""

#calculate all URI and ESL values

#%% read packages
import pandas as pd
import numpy as np
import geopandas as gpd
from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()


def calculate_ABS(list_abbrev_haz):

    list_geo = ['BOROCODE', 'PUMA', 'NTA', 'BCT_txt']
    list_geo_folder = ['Borough', 'PUMA', 'NTA', 'Tract']
    list_geo_keep = []
    for (geo_id, geo_name) in zip(list_geo, list_geo_folder):
        print(geo_name, end=' ')
        #list_geo_keep.append(geo_id)

        #%% open and stack all URI shapefiles
        for i, haz in enumerate(list_abbrev_haz):
            path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
            gdf_this = gpd.read_file(path_haz)
            gdf_this['Haz'] = np.repeat(haz, len(gdf_this))
            #remove hazard name from column titles so they can be stacked
            gdf_this.columns = [x.replace(haz, '') for x in gdf_this.columns]
            if i==0:
                gdf_stack = gdf_this.copy()
            else:
                gdf_stack = gdf_stack.append(gdf_this)

        #%% calculate score and percentile
        gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='E_RNTT', score_column='E_ANTT')
        gdf_stack = utils.calculate_percentile(gdf_stack, data_column='E_RNTT', score_column='E_QNTT')

        gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='U_RN', score_column='U_AN')
        gdf_stack = utils.calculate_percentile(gdf_stack, data_column='U_RN', score_column='U_QN')

        #%% add absolute value to each URI shapefile
        for i, haz in enumerate(list_abbrev_haz):
            path_uri = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
            gdf_uri = gpd.read_file(path_uri)
            this_haz = gdf_stack.loc[gdf_stack['Haz']==haz].copy()[[geo_id] + [ 'E_ANTT', 'E_QNTT', 'U_AN', 'U_QN']]
            this_haz.columns = [x.replace('E_', haz + 'E_') for x in this_haz.columns]
            this_haz.columns = [x.replace('U_', haz + 'U_') for x in this_haz.columns]
            gdf_uri = gdf_uri.merge(this_haz, on=geo_id, how='inner')
            gdf_uri.to_file(path_uri)

#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list
    folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()
    list_abbrev_haz.remove('CYB')
    list_abbrev_haz = list_abbrev_haz[0:2]

    calculate_ABS(list_abbrev_haz)