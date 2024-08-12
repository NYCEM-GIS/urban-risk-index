""" combine calculations for RCA score"""


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% calculate RCA
def calculate_RCA(haz):

    # %% open tract
    gdf_tract = utils.get_blank_tract()
    list_col_keep = ['BCT_txt', 'geometry']
    #find codes and their components with valid data
    list_code = params.MITIGATION.loc[:, 'Factor Code'].values
    list_component = params.MITIGATION.loc[:, 'Component Code'].values
    list_component_name = params.MITIGATION.loc[:, 'RC Component'].values
    
    # Load hazard specipic only rows where weight > 0
    list_code_valid = []
    list_code_weight = []
    list_component_valid = []
    list_haz_specific_valid = []
    applicable_fo_haz_df = params.MITIGATION[params.MITIGATION[haz] > 0]
    list_code_valid = applicable_fo_haz_df['Factor Code'].values
    list_component_valid = applicable_fo_haz_df['Component Code'].values
    list_code_weight = applicable_fo_haz_df[haz].values
    list_haz_specific_valid = applicable_fo_haz_df['Hazard Specific'].values

    #add all valid codes into gdf
    for j in np.arange(len(list_code_valid)):
        code = list_code_valid[j]
        component = list_component_valid[j]
        haz_specific = list_haz_specific_valid[j]
        path_score = getattr(PATHNAMES, 'RCA_{}_{}_score'.format(component, code))
        if haz_specific == 'No':
            source_column_name = 'Score'
        elif haz_specific == 'Yes':
            source_column_name = 'Score_{}'.format(haz)
        target_column_name = '{}_{}'.format(component, code)
        gdf_score = gpd.read_file(path_score)
        gdf_tract = gdf_tract.merge(gdf_score[['BCT_txt', source_column_name]], on='BCT_txt', how='left' )
        gdf_tract.rename(columns={source_column_name:target_column_name}, inplace=True)
        list_col_keep.append(target_column_name)

    # calculate subcomponents
    list_component_uniq = list(dict.fromkeys(list_component))
    for component in list_component_uniq:
        if component in list_component_valid:
            output = [idx for idx, comp in enumerate(list_component_valid) if comp==component]
            this_code = ['{}_'.format(component) + list_code_valid[x] for x in output]
            this_code_weight = [list_code_weight[x] for x in output]
            gdf_tract['{}'.format(component)] = np.average(gdf_tract.loc[:, this_code], weights=this_code_weight, axis=1)        
            
        else:
            gdf_tract['{}'.format(component)] = np.zeros(len(gdf_tract))

        list_col_keep.append('{}'.format(component))

    #calculate final RCA
    #CHANGE TO divede by 4.0 when RC data is available
    gdf_tract['RCA'] = gdf_tract.loc[:, list_component_uniq].sum(axis=1)/len(np.unique(list_component_valid))
    list_col_keep.append('RCA')

    #%% rename columns
    gdf_tract = gdf_tract[list_col_keep].copy()
    for col in gdf_tract.columns:
        if len(col)==2:
            gdf_tract.rename(columns={col:haz+'R_R'+col + 'TT'}, inplace=True)
        elif len(col)==3:
            gdf_tract.rename(columns={col: haz + 'R_R' + 'TTTT'}, inplace=True)
        elif len(col)==5:
            gdf_tract.rename(columns={col: haz + 'R_R' + col.replace('_', '')}, inplace=True)

    #%% calculate score and percentile
    list_R_col = [col for col in gdf_tract.columns if 'R_R' in col]
    for col in list_R_col:
        score_col = col[0:5] + 'S' + col[6:]
        #gdf_tract = utils.calculate_kmeans(gdf_tract, data_column=col, score_column=score_col)
        gdf_tract[score_col] = [np.round(x, 0) for x in gdf_tract[col]]
        percentile_col = col[0:5] + 'P' + col[6:]
        gdf_tract = utils.calculate_percentile(gdf_tract, data_column=col, score_column=percentile_col)

    #%% plot in notebook
    list_component_name_uniq = list(dict.fromkeys(list_component_name))
    dct_component = {list_component_uniq[x]: list_component_name_uniq[x] for x in range(len(list_component_uniq))}

    for code in dct_component.keys():
        name = dct_component[code]
        plotting.plot_notebook(gdf_tract, column=haz+'R_S'+code+'TT', title=haz + ': ' + name,
                               legend='Score', cmap='Blues', type='score')
    plotting.plot_notebook(gdf_tract, column=haz + 'R_S' + 'TTTT', title=haz + ': Total Resilience Capacity',
                           legend='Score', cmap='Blues', type='score')

    #%%

    # save as output
    path_output = PATHNAMES.OUTPUTS_folder + r'\\RCA\\Tract\\RCA_{}_Tract.shp'.format(haz)
    gdf_tract.to_file(path_output)

    #  document result with readme
    try:
        text = """ 
        The data was produced by {}
        Located in {}
        """.format(os.path.basename(__file__), os.path.dirname(__file__))
        path_readme = os.path.dirname(path_output)
        utils.write_readme(path_readme, text)
    except:
        pass

    # output complete message
    print("Finished calculating RCA factor for {}.".format(haz))


#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list and mitigation table
    folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()

    #run script
    #for haz in list_abbrev_haz[0:2]:
    #    calculate_RCA(haz)
    haz='FLD'
    calculate_RCA(haz)














