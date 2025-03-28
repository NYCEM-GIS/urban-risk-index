""" calculate absolute scores and percentiles for each hazard for total loss and total risk"""

#calculate all URI and ESL values

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()


def calculate_ABS(list_abbrev_haz):

    list_geo = ['borocode', 'cdta2020', 'nta2020', 'BCT_txt']
    list_geo_folder = ['Borough', 'CDTA', 'NTA', 'Tract']
    list_geo_keep = []
    for (geo_id, geo_name) in zip(list_geo, list_geo_folder):
        print(geo_name, end=' ')
        #list_geo_keep.append(geo_id)

        #%% open and stack all URI shapefiles
        for i, haz in enumerate(list_abbrev_haz):
            path_haz = PATHNAMES.OUTPUTS_folder + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
            gdf_this = gpd.read_file(path_haz)
            gdf_this['Haz'] = np.repeat(haz, len(gdf_this))
            #remove hazard name from column titles so they can be stacked
            gdf_this.columns = [x.replace(haz, '') for x in gdf_this.columns]
            if i==0:
                gdf_stack = gdf_this.copy()
            else:
                gdf_stack = pd.concat([gdf_stack, gdf_this])

        #%% calculate score and percentile
        gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='E_RNTT', score_column='E_ANTT')
        gdf_stack = utils.calculate_percentile(gdf_stack, data_column='E_RNTT', score_column='E_QNTT')

        gdf_stack = utils.calculate_kmeans(gdf_stack, data_column='U_RN', score_column='U_AN')
        gdf_stack = utils.calculate_percentile(gdf_stack, data_column='U_RN', score_column='U_QN')

        #%% add absolute value to each URI shapefile
        for i, haz in enumerate(list_abbrev_haz):
            path_uri = PATHNAMES.OUTPUTS_folder + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
            gdf_uri = gpd.read_file(path_uri)
            this_haz = gdf_stack.loc[gdf_stack['Haz']==haz].copy()[[geo_id] + [ 'E_ANTT', 'E_QNTT', 'U_AN', 'U_QN']]
            this_haz.columns = [x.replace('E_', haz + 'E_') for x in this_haz.columns]
            this_haz.columns = [x.replace('U_', haz + 'U_') for x in this_haz.columns]
            gdf_uri = gdf_uri.merge(this_haz, on=geo_id, how='inner')
            gdf_uri.to_file(path_uri)
            #plot
            if geo_name=='Tract':
                plotting.plot_notebook(gdf_uri, column=haz + 'U_AN', title=haz + ': Absolute Urban Risk Index',
                                       legend='Score', cmap='Purples', type='score')


#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list
    folder_outputs = PATHNAMES.OUTPUTS_folder
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()
    list_abbrev_haz.remove('CYB')
    list_abbrev_haz = ['EXH', 'WIW']

    calculate_ABS(list_abbrev_haz)