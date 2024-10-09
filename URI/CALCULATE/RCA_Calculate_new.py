""" combine calculations for RCA score"""


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% calculate RCA
def calculate_RCA(haz):
    if haz == 'COR':
        resilience_df_path = PATHNAMES.community_resilience_path
    else:
        resilience_df_path = PATHNAMES.hazard_resilience_path 
    
    resilience_df = pd.read_csv(resilience_df_path)

    # %% open tract
    gdf_tract = utils.get_blank_tract()
    list_col_keep = ['BCT_txt', 'geometry']
   
    #find codes and their components with valid data
    ### Load hazard specipic only rows where weight > 0
    applicable_to_haz_df = resilience_df[resilience_df[haz] > 0]
    applicable_to_haz_df['source_column_name'] = applicable_to_haz_df.apply(
        lambda row: f'Score_{haz}' if row['Specific'] else 'Score', 
        axis=1)
    applicable_to_haz_df['target_column_name'] = applicable_to_haz_df['Subcomponent'] + '_' + applicable_to_haz_df['Factor']
    
    # add all valid codes into gdf
    for index, row in applicable_to_haz_df.iterrows():
        path_score = getattr(PATHNAMES, f'RCA_{row["Subcomponent"]}_{row["Factor"]}_score')
        gdf_score = gpd.read_file(path_score)
        gdf_tract = gdf_tract.merge(gdf_score[['BCT_txt', row['source_column_name']]], on='BCT_txt', how='left' )
        gdf_tract.rename(columns={row['source_column_name']:row['target_column_name']}, inplace=True)
        list_col_keep.append(row['target_column_name'])

    # # calculate subcomponents
    list_component_uniq =  resilience_df['Subcomponent'].unique().tolist()

    #calculate final RCA
    average_col = haz + 'R_RTTTT'
    score_col = haz + 'R_STTTT'
    gdf_tract[average_col] = gdf_tract[applicable_to_haz_df['target_column_name'].values].mean(axis=1)
    list_col_keep.append(average_col)
    gdf_tract = utils.calculate_kmeans(gdf_tract, data_column=average_col, score_column=score_col)

    #%% plot in notebook
    plotting.plot_notebook(gdf_tract, column=average_col, title=haz + ': Average Resilience Capacity',
                           legend='Score', cmap='Blues', type='raw')
    plotting.plot_notebook(gdf_tract, column=score_col, title=haz + ': Total Resilience Capacity',
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
