#%% read packages
import numpy as np
import geopandas as gpd
import URI.MISC.plotting_1 as plotting
import URI.MISC.utils_1 as utils
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% define functions
def weight_ave(x, weights):
    if weights.sum() != 0:
        result = np.average(x, weights=weights)
    else:
        result = 3
    return result

#%%
def calculate_URI(haz):

    print('Calculating {}'.format(haz))
    # open SOV, RCA, ESL
    path_ESL = PATHNAMES.OUTPUTS_folder + r'\ESL\Tract\\ESL_{}_tract.shp'.format(haz)
    gdf_ESL = gpd.read_file(path_ESL)

    path_SOV = PATHNAMES.OUTPUTS_folder + r'\SOV\Tract\\SOV_tract.shp'
    df_SOV = gpd.read_file(path_SOV)
    df_SOV.drop(columns=['geometry'], inplace=True)

    path_RCA = PATHNAMES.OUTPUTS_folder + r'\RCA\Tract\\RCA_{}_tract.shp'.format(haz)
    df_RCA = gpd.read_file(path_RCA)
    df_RCA.drop(columns=['geometry'], inplace=True)

    path_COR = PATHNAMES.OUTPUTS_folder + r'\RCA\Tract\\RCA_COR_tract.shp'
    df_COR = gpd.read_file(path_COR)
    df_COR.drop(columns=['geometry'], inplace=True)


    #%% assemble into single file and calculate URI
    gdf_URI = gdf_ESL.copy()
    gdf_URI = gdf_URI.merge(df_RCA, on='BCT_txt', how='left')
    gdf_URI = gdf_URI.merge(df_SOV, on='BCT_txt', how='left')
    gdf_URI = gdf_URI.merge(df_COR, on='BCT_txt', how='left')

    #%% calculate URI
    raw_col = haz + 'U_RN'
    score_col = haz + 'U_SN'
    gdf_URI[raw_col] = gdf_URI[haz+'E_RXXT'] / gdf_URI[haz+'R_RTTTT'] * gdf_URI['S_R'] # / gdf_URI['CORR_RTTTT']
    gdf_URI = gdf_URI.fillna(0)
    gdf_URI = utils.calculate_kmeans(gdf_URI, data_column=raw_col, score_column=score_col)


    #%% plot results
    plotting.plot_notebook(gdf_URI, column=raw_col, title=haz + ': Raw Urban Risk Index',
                           legend='Score', cmap='Purples', type='raw')
    plotting.plot_notebook(gdf_URI, column=score_col, title=haz + ': Urban Risk Index Score',
                           legend='Score', cmap='Purples', type='score')

    #%% save in Tract
    path_save_tract = PATHNAMES.OUTPUTS_folder + r'\URI\Tract\URI_{}_Tract.shp'.format(haz, haz)
    gdf_URI.to_file(path_save_tract)

