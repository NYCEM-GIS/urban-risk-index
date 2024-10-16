""" Calculate the total loss for each hazard"""

#%% read packages
import numpy as np
import geopandas as gpd
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
import pandas as pd
utils.set_home()


#%% calculate ESL
def calculate_ESL(haz):
    print('Calculating {}'.format(haz))

    # load data
    df_norm = gpd.read_file(PATHNAMES.OTH_normalize_values)
    consequences_df = pd.read_csv(PATHNAMES.consequences_path)
    gdf_ESL = utils.get_blank_tract()
    # merge normalization factors
    df_norm.drop(columns={'geometry'}, inplace=True)
    gdf_ESL = gdf_ESL.merge(df_norm, on='BCT_txt', how='left')

    receptor_dict = {'A': 'AREA_SQMI', 'F': 'FLOOR_SQFT', 'P': 'POP', 'O': 'ONE'}

    #%%get factors, abbreviateions, path names
    #get lookup table for subcomponents
    df_cons = consequences_df[consequences_df['Hazard'] == haz]

    print(".....Importing {} expected annual losses.....".format(haz))
    print(" ")
    df_cons["Raw_col"] = haz + 'E_RN' + df_cons['Subcomponent'] + df_cons['Factor']
    df_cons['Normalized_col'] = haz + 'E_R' + df_cons['Receptor'] + df_cons['Subcomponent'] + df_cons['Factor']
    df_cons['Score_col'] = df_cons["Normalized_col"].str.replace('E_R', 'E_S')
    df_cons['Percentile_col'] = df_cons["Normalized_col"].str.replace('E_R', 'E_P')
    for idx in df_cons.index:
        this_abbrv = df_cons.at[idx, 'Factor']
        this_receptor = df_cons.at[idx, 'Receptor']
        receptor_field = receptor_dict[this_receptor]
        this_subcomponent_abbrv = df_cons.at[idx, 'Subcomponent']
        this_path = df_cons.at[idx, 'Path_Name']
        raw_col = df_cons.at[idx, 'Raw_col']
        normalized_col = df_cons.at[idx, 'Normalized_col']
        score_col = df_cons.at[idx, 'Score_col']
        percentile_col = df_cons.at[idx, 'Percentile_col']
        print("..........Abbreviation:  {}".format(this_abbrv))
        print("..........Receptor:  {}".format(this_receptor))
        print("..........Category:  {}".format(this_subcomponent_abbrv))
        print(" ")
        # add consequence
        path_consequence = getattr(PATHNAMES, this_path)
        gdf_consequence = gpd.read_file(path_consequence)[['BCT_txt', 'Loss_USD']]
        gdf_consequence.rename(columns={"Loss_USD":raw_col}, inplace=True)
        gdf_ESL = gdf_ESL.merge(gdf_consequence, on='BCT_txt', how='left')
        gdf_ESL = gdf_ESL.fillna(0)
        gdf_ESL[normalized_col] = gdf_ESL.apply(
            lambda row: utils.divide_zero(row[raw_col], row[receptor_field]), axis=1)
        gdf_ESL = utils.calculate_percentile(gdf_ESL, data_column=normalized_col, score_column=percentile_col)
        gdf_ESL = utils.calculate_kmeans(gdf_ESL, data_column=normalized_col, score_column=score_col)

        plotting.plot_notebook(gdf_ESL, column=raw_col, title=haz + ' Raw Value: ' + this_path,
                               legend='Loss USD', cmap='Greens', type='raw')
        plotting.plot_notebook(gdf_ESL, column=normalized_col, title=haz + ' Normalized Value: ' + this_path,
                        legend='Normalized Value', cmap='Greens', type='raw')
        plotting.plot_notebook(gdf_ESL, column=percentile_col, title=haz + ' Percentile: ' + this_path,
                        legend='Percentile', cmap='Greens', type='raw')
        plotting.plot_notebook(gdf_ESL, column=score_col, title=haz + ' Normalized Score: ' + this_path,
                        legend='Score', cmap='Greens', type='score')
    # rename the columns in new Boundary tract file.    
    list_all_col = df_cons["Raw_col"].to_list() + df_cons['Normalized_col'].to_list() + df_cons['Score_col'].to_list()  + df_cons['Percentile_col'].to_list() + ['BCT_txt', 'geometry', 'borocode', 'nta2020', 'cdta2020']
    gdf_ESL = gdf_ESL[list_all_col]

    #%% get total sum
    score_sum_col = haz + 'E_RXXT'
    gdf_ESL[score_sum_col] = gdf_ESL[df_cons["Score_col"].to_list()].sum(axis=1)
    # Fill na wil 0 in gdf_ESL
    gdf_ESL = gdf_ESL.fillna(0)
    final_score_col = haz + 'E_SXXS'
    gdf_ESL = utils.calculate_kmeans(gdf_ESL, data_column=score_sum_col, score_column=final_score_col)


    plotting.plot_notebook(gdf_ESL, column=final_score_col, title=haz + ': Total Loss Score',
                           legend='Score', cmap='Greens', type='score')


    #%%
    path_save = PATHNAMES.OUTPUTS_folder + r'\ESL\Tract\ESL_{}_Tract.shp'.format(haz, haz)
    gdf_ESL.to_file(path_save)

