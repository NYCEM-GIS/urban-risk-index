""" upscale results to calculate for NTA, CDTA, """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.plotting_1 as plotting
import URI.UTILITY.utils_1 as utils
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% define weighted avereage
def weight_ave(x, weights):
    if weights.sum() != 0:
        result = np.average(x, weights=weights)
    else:
        result = np.average(x)  # return non-population weighted average rather than value of 3
    return result

def calculate_UPSCALE(haz):
    print('Upscaling {}.....'.format(haz), end="")

    #%% open tract uri
    path_uri = PATHNAMES.OUTPUTS_folder + r'\URI\Tract\URI_{}_tract.shp'.format(haz)
    gdf_uri = gpd.read_file(path_uri)

    #%% create tract and master
    gdf_tract = utils.get_blank_tract()

    path_norm = PATHNAMES.OTH_normalize_values
    df_norm = gpd.read_file(path_norm)
    df_norm.drop(columns={'geometry'}, inplace=True)
    gdf_tract = gdf_tract.merge(df_norm, on='BCT_txt', how='left')
    gdf_uri = gdf_uri.merge(df_norm, on='BCT_txt', how='left')
    # add borough name
    path_boro = PATHNAMES.Borough_to_FIP
    df_boro = pd.read_excel(path_boro)
    df_boro['borocode'] = [str(x) for x in df_boro['Bor_ID']]
    gdf_tract = gdf_tract.merge(df_boro[['Borough', 'borocode']], left_on='borocode', right_on='borocode', how='left' )

    #%% select upscale key
    list_geo = ['borocode', 'cdta2020', 'nta2020']
    list_geo_folder = ['Borough', 'CDTA', 'NTA']
    list_geo_keep = []
    for (geo_id, geo_name) in zip(list_geo, list_geo_folder):
        print(geo_name, end=' ')
        list_geo_keep.append(geo_id)

        #%% get new dissolved shapefile with only geo_id
        gdf_new = gdf_uri.copy()
        gdf_new  = gdf_new[list_geo_keep + ['geometry']].dissolve(by=geo_id)
        gdf_new[geo_id] = gdf_new.index
        gdf_new.index.name = 'Index'

        #add normalization to new gdf
        df_norm = gdf_tract.copy()[[geo_id, 'AREA_SQMI', 'BLD_CNT', 'FLOOR_SQFT', 'POP']]
        df_agg = df_norm.groupby(by=geo_id).sum()
        gdf_new = gdf_new.merge(df_agg, left_on=geo_id, right_index=True, how='left')
        gdf_new['Geography'] = geo_name
        gdf_new['Boro_Name'] = np.nan

        #%% get sum of losses, risk scores, and normalization factors and merge
        list_col_loss = [col for col in gdf_uri.columns if 'E_RN' in col]
        list_col_uri = [col for col in gdf_uri.columns if 'U_RN' in col]
        list_col_keep = [geo_id] + list_col_loss + list_col_uri
        df_sum = gdf_uri[list_col_keep].groupby(by=geo_id).sum()
        gdf_new = gdf_new.merge(df_sum, left_on=geo_id, right_index=True, how='left')

        #%% get pop weighted average of SOV and RCA raw scores, merge
        gdf_uri.index = np.arange(len(gdf_uri))
        wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "POP"])
        list_col_wm = [geo_id, 'S_R'] + [col for col in gdf_uri.columns if 'R_R' in col] + [col for col in gdf_uri.columns if 'E_RXXT' in col]
        df_wm = gdf_uri[list_col_wm].groupby(by=geo_id).agg(wm)
        gdf_new = gdf_new.merge(df_wm, left_on=geo_id, right_index=True, how='left')

        # %% calculate scores
        list_col = ['S_R'] + [col for col in gdf_new.columns if haz in col[0:3]]
        for col in list_col:
            if col == 'S_R':
                score_col = 'S_S'
                percentile_col = 'S_P'
                gdf_new[score_col] = [np.round(x, 0) for x in gdf_new[col]]
                gdf_new = utils.calculate_percentile(gdf_new, data_column=col, score_column=percentile_col)
            elif col[3:5]=='R_':
                score_col = col[0:5] + 'S' + col[6:]
                percentile_col = col[0:5] + 'P' + col[6:]
                gdf_new = utils.calculate_kmeans(gdf_new, data_column=col, score_column=score_col)
                gdf_new = utils.calculate_percentile(gdf_new, data_column=col, score_column=percentile_col)
            else:
                score_col = col[0:5] + 'S' + col[6:]
                percentile_col = col[0:5] + 'P' + col[6:]
                gdf_new = utils.calculate_kmeans(gdf_new, data_column=col, score_column=score_col)
                gdf_new = utils.calculate_percentile(gdf_new, data_column=col, score_column=percentile_col)

        #%% save in Tract
        path_output = PATHNAMES.OUTPUTS_folder + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
        gdf_new.to_file(path_output)

        #%% plot
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
