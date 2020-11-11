""" combine calculations for RCA score"""


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% open outputs path and get abbrev list and mitigation table
folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
list_abbrev = params.ABBREVIATIONS.iloc[0:11, 0].values

#%% open tract
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

#%% calculate RCA
for i, haz in enumerate(list_abbrev):

    #find codes and their components with valid data
    list_code = params.MITIGATION.loc[:, 'Factor Code'].values
    list_component = params.MITIGATION.loc[:, 'Component Code'].values
    list_haz_specific = params.MITIGATION.loc[:, 'Hazard Specific'].values
    list_code_valid = []
    list_component_valid = []
    list_haz_specific_valid = []
    for j, code in enumerate(list_code):
        component = list_component[j]
        haz_specific = list_haz_specific[j]
        try:
            path_score = params.PATHNAMES.at['RCA_{}_{}_score'.format(component, code), 'Value']
            if params.MITIGATION.loc[params.MITIGATION['Factor Code']==code, haz].values[0]==1:
                list_code_valid.append(code)
                list_component_valid.append(component)
                list_haz_specific_valid.append(haz_specific)
        except:
            print("Missing score for code {}".format(code))

    #add all valid codes into gdf
    for j in np.arange(len(list_code_valid)):
        code = list_code_valid[j]
        component = list_component_valid[j]
        haz_specific = list_haz_specific_valid[j]
        path_score = params.PATHNAMES.at['RCA_{}_{}_score'.format(component, code), 'Value']
        if haz_specific == 'No':
            source_column_name = 'Score'
        elif haz_specific == 'Yes':
            source_column_name = 'Score_{}'.format(haz)
        target_column_name = '{}_{}'.format(component, code)
        gdf_score = gpd.read_file(path_score)
        gdf_tract = gdf_tract.merge(gdf_score[['BCT_txt', source_column_name]], on='BCT_txt', how='left' )
        gdf_tract.rename(columns={source_column_name:target_column_name}, inplace=True)

    # calculate subcomponents
    list_component_uniq = np.unique(list_component)
    for j, component in enumerate(list_component_uniq):
        output = [idx for idx, comp in enumerate(list_component_valid) if comp==component]
        this_code = ['{}_'.format(component) + list_code_valid[x] for x in output]
        if len(this_code)==0:
            gdf_tract['{}'.format(component)] = np.zeros(len(gdf_tract))
        else:
            gdf_tract['{}'.format(component)] = gdf_tract.loc[:, this_code].sum(axis=1)/len(this_code)

    #calculate final RCA
    gdf_tract['RCA'] = gdf_tract.loc[:, list_component_uniq].sum(axis=1)/4.0

    # save as output
    path_output = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\\{}\\{}_RCA_tract.shp'.format(haz, haz)
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

















