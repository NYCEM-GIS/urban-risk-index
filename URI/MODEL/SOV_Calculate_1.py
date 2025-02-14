"""
get CDC SOVI score for each tract.
Normalize for NEW to scale between 0 and 100 using percent ranking

"""

#%%% import packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES

utils.set_home()

def calculate_SOV():

    #%% EXTRACT PARAMETERS
    path_sovi = PATHNAMES.SOV_tract
    path_FIPS = PATHNAMES.Borough_to_FIP

    #%% LOAD DATA
    df_FIPS = pd.read_excel(path_FIPS, index_col='FIPS')
    path_layer = os.path.basename(path_sovi)
    path_gdb = os.path.dirname(path_sovi)
    gdf_sovi = gpd.read_file(path_gdb, driver='FileGDB', layer=path_layer)
    
    df_FIPS.index = df_FIPS.index.astype(str)
    gdf_tract = utils.project_gdf(gdf_sovi)
    gdf_tract = gdf_tract.merge(df_FIPS, left_on='STCNTY', right_index=True, how='inner')

    # Creating BCT_txt column from FIPS
    gdf_tract['BCT_txt'] = gdf_tract['Bor_ID'].astype(str) + gdf_tract['FIPS'].str[5:11]

    #%% normalize result to scale of 0.01 to 0.99
    gdf_tract['SOV_rank'] = utils.normalize_rank_percentile(gdf_tract['RPL_THEMES'].values,
                                                            list_input_null_values=[0, -999],
                                                            output_null_value=0)
    gdf_tract['S_R'] = 1 + gdf_tract['SOV_rank'] / 0.25

    #%% calculate percentile and score
    #gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='S_R', score_column='S_S')
    gdf_tract['S_S'] = [np.round(x, 0) for x in gdf_tract['S_R']]
    gdf_tract = utils.calculate_percentile(gdf_tract, data_column='S_R', score_column='S_P')

    #%% plot results
    plotting.plot_notebook(gdf_tract, column='S_S', title='ALL: Social Vulnerability',
                           legend='Score', cmap='Reds', type='score')

    #%% save results in every folder (same for all)
    path_results = PATHNAMES.OUTPUTS_folder + r'\\SOV\Tract\\SOV_Tract.shp'
    gdf_tract[['BCT_txt', 'S_R', 'S_S', 'S_P', 'geometry']].to_file(path_results)

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
    print("Finished calculating SOV score.")


#%% main
if __name__ == '__main__':
    #run script
    calculate_SOV()