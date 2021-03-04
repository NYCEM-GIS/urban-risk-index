""" upscale results to calculate for NTA, PUMA, """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

import URI.MISC.plotting_1 as plotting
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
utils.set_home()

#%% define weighted avereage
def weight_ave(x, weights):
    if weights.sum() != 0:
        result = np.average(x, weights=weights)
    else:
        result = 3
    return result

def calculate_UPSCALE(haz):
    print('Upscaling {}.....'.format(haz), end="")

    #%% open tract uri
    path_uri = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format(haz)
    gdf_uri = gpd.read_file(path_uri)

    #%% select upscale key
    list_geo = ['CITYWIDE', 'BOROCODE', 'PUMA', 'NTA', ]
    list_geo_folder = ['CITYWIDE', 'Borough', 'PUMA', 'NTA']
    list_geo_keep = []
    for (geo_id, geo_name) in zip(list_geo, list_geo_folder):
        print(geo_name, end=' ')
        list_geo_keep.append(geo_id)
        # add citywide id
        gdf_uri['CITYWIDE'] = [int(1) for x in np.arange(len(gdf_uri))]

        #%% get new dissolved shapefile with only geo_id
        gdf_new = gdf_uri.copy()
        gdf_new.geometry = gdf_new.buffer(0)
        gdf_new  = gdf_new[list_geo_keep + ['geometry']].dissolve(by=geo_id)
        gdf_new[geo_id] = gdf_new.index
        gdf_new.index.name = 'Index'
        path_new = params.PATHNAMES.at['TBL_B_shp', 'Value']
        gdf_new.to_file(path_new)

        #%% get sum of losses, risk scores, and normalization factors and merge
        list_col_norm = ['AREA_SQMI', 'FLOOR_SQFT', 'POP', 'BLD_CNT']
        list_col_loss = [col for col in gdf_uri.columns if 'E_RN' in col]
        list_col_uri = [col for col in gdf_uri.columns if 'U_RN' in col]
        list_col_keep = [geo_id] + list_col_norm + list_col_loss + list_col_uri
        df_sum = gdf_uri[list_col_keep].groupby(by=geo_id).sum()
        gdf_new = gdf_new.merge(df_sum, left_on=geo_id, right_index=True, how='left')

        #%% if haz==ALL and geo_id==CITYWIDE, add in CYB losses and URI score
        if haz=='ALL':
            if geo_id=='CITYWIDE':
                path_CYB = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format('CYB')
                gdf_CYB = gpd.read_file(path_CYB)
                list_col_add = [col for col in gdf_new.columns if (('E_RN' in col) or ('U_RN' in col))]
                for col in list_col_add:
                    gdf_new[col] = gdf_new[col] + gdf_CYB[col.replace('ALL', 'CYB')].sum()

        #%% get pop weighted average of SOV and RCA raw scores, merge
        gdf_uri.index = np.arange(len(gdf_uri))
        wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "POP"])
        list_col_wm = [geo_id, 'S_R'] + [col for col in gdf_uri.columns if 'R_R' in col]
        df_wm = gdf_uri[list_col_wm].groupby(by=geo_id).agg(wm)
        gdf_new = gdf_new.merge(df_wm, left_on=geo_id, right_index=True, how='left')

        #%% calculate normalization values
        list_norm_col = ['AREA_SQMI', 'FLOOR_SQFT', 'POP']
        list_abbrv = ['A', 'F', 'P']
        list_col = [col for col in gdf_new.columns if (('E_RN' in col) or ('U_RN' in col))]
        for norm, abbrv in zip(list_norm_col, list_abbrv):
            for col in list_col:
                new_col = col[0:6] + abbrv + col[7:]
                gdf_new[new_col] = gdf_new.apply(lambda row: utils.divide_zero(row[col], row[norm]), axis=1)

        # %% calculate scores
        list_col = ['S_R'] + [col for col in gdf_new.columns if haz in col[0:3]]
        for col in list_col:
            score_col = col[0:5] + 'S' + col[6:]
            gdf_new = utils.calculate_kmeans(gdf_new, data_column=col, score_column=score_col)
            percentile_col = col[0:5] + 'P' + col[6:]
            gdf_new = utils.calculate_percentile(gdf_new, data_column=col, score_column=percentile_col)

        #%% delete CITYWIDE
        if geo_id=='CITYWIDE': gdf_new.drop(columns={'CITYWIDE'}, inplace=True)

        #%% save in Tract
        path_output = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
        gdf_new.to_file(path_output)

        #%% plot
        if geo_name != 'CITYWIDE':
            plotting.plot_notebook(gdf_new, column=haz+'U_SN', title=haz + ': Urban Risk Index ({})'.format(geo_name),
                                   legend='Score', cmap='Purples', type='score')


        #%%  document result with readme
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(path_output)
            utils.write_readme(path_readme, text)
        except:
            pass
    print("Done.")

#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list
    folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()

    #run script
    for haz in list_abbrev_haz[0:2]:
        calculate_UPSCALE(haz)


