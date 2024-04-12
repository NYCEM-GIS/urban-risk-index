#%% read packages
import numpy as np
import geopandas as gpd
import URI.MISC.plotting_1 as plotting
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
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
    path_ESL = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\ESL\Tract\\ESL_{}_tract.shp'.format(haz, haz)
    gdf_ESL = gpd.read_file(path_ESL)

    path_SOV = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\SOV\Tract\\SOV_tract.shp'.format( haz)
    df_SOV = gpd.read_file(path_SOV)
    df_SOV.drop(columns={'geometry'}, inplace=True)

    path_RCA = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\RCA\Tract\\RCA_{}_tract.shp'.format(haz, haz)
    df_RCA = gpd.read_file(path_RCA)
    df_RCA.drop(columns={'geometry'}, inplace=True)

    #%% assemble into single file and calculate URI
    gdf_URI = gdf_ESL.copy()
    gdf_URI = gdf_URI.merge(df_RCA, on='BCT_txt', how='left')
    gdf_URI = gdf_URI.merge(df_SOV, on='BCT_txt', how='left')

    #%% calculate URI
    gdf_URI[haz + 'U_RN'] = gdf_URI[haz+'E_RNTT'] * gdf_URI['S_R'] / gdf_URI[haz+'R_RTTTT']

    #%% calculate normalization
    def divide_zero(x, y):
        if y == 0:
            return 0
        else:
            return x / y
    list_norm_col = ['AREA_SQMI', 'FLOOR_SQFT', 'POP']
    list_abbrv = ['A', 'F', 'P']
    for norm, abbrv in zip(list_norm_col, list_abbrv):
        list_col = [col for col in gdf_URI if 'U_RN' in col]
        for col in list_col:
            new_col = col[0:6] + abbrv
            gdf_URI[new_col] = gdf_URI.apply(lambda row: divide_zero(row[col], row[norm]), axis=1)

    # %% calculate scores
    list_col = [col for col in gdf_URI if 'U_R' in col]

    for col in list_col:
        score_col = col[0:5] + 'S' + col[6:]
        gdf_URI = utils.calculate_kmeans(gdf_URI, data_column=col, score_column=score_col)
        percentile_col = col[0:5] + 'P' + col[6:]
        gdf_URI = utils.calculate_percentile(gdf_URI, data_column=col, score_column=percentile_col)

    #%% plot results
    plotting.plot_notebook(gdf_URI, column=haz + 'U_SN', title=haz + ': Urban Risk Index',
                           legend='Score', cmap='Purples', type='score')

    #%% save in Tract
    path_save_tract = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_Tract.shp'.format(haz, haz)
    gdf_URI.to_file(path_save_tract)


#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list and mitigation table
    folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()

    #run script
    for haz in list_abbrev_haz[0:2]:
        calculate_URI(haz)

