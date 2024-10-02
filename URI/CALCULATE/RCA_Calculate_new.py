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
    if haz == 'RCA':
        resilience_df_path = PATHNAMES.Resilience_Capacity_path
        resilience_df = pd.read_csv(resilience_df_path)

    else:
        resilience_df_path = PATHNAMES.Hazard_Resilience_Capacity_path 
        resilience_df = pd.read_csv(resilience_df_path,skiprows=1)

    # %% open tract
    gdf_tract = utils.get_blank_tract()
    list_col_keep = ['BCT_txt', 'geometry']
   
    #find codes and their components with valid data
    ### Load hazard specipic only rows where weight > 0
    applicable_to_haz_df = resilience_df[resilience_df[haz] > 0]
    applicable_to_haz_df['source_column_name'] = applicable_to_haz_df.apply(lambda row: 'Score' if row['Hazard Specific'] == 'No' else 'Score_{}'.format(haz), axis=1)
    applicable_to_haz_df['target_column_name'] = applicable_to_haz_df['Component Code']+'_'+applicable_to_haz_df['Factor Code']
    
    # add all valid codes into gdf
    for index, row in applicable_to_haz_df.iterrows():
        path_score = getattr(PATHNAMES, 'RCA_{}_{}_score'.format(row['Component Code'], row['Factor Code']))
        gdf_score = gpd.read_file(path_score)
        gdf_tract = gdf_tract.merge(gdf_score[['BCT_txt', row['source_column_name']]], on='BCT_txt', how='left' )
        gdf_tract.rename(columns={row['source_column_name']:row['target_column_name']}, inplace=True)
        list_col_keep.append(row['target_column_name'])
    

    # calculate subcomponents
    list_component_uniq =  resilience_df['Component Code'].unique().tolist()

    for component in list_component_uniq:
        if component in applicable_to_haz_df['Component Code'].tolist():
            condition = applicable_to_haz_df['Component Code'] == component
            this_code = applicable_to_haz_df[condition]['target_column_name'].tolist()
            this_code_weight = applicable_to_haz_df[condition][haz].tolist()
            gdf_tract['{}'.format(component)] = np.average(gdf_tract.loc[:, this_code], weights=this_code_weight, axis=1)        
            
        else:
            gdf_tract['{}'.format(component)] = np.zeros(len(gdf_tract))

        list_col_keep.append('{}'.format(component))

    #calculate final RCA
    #CHANGE TO divede by 4.0 when RC data is available
    gdf_tract['RCA'] = gdf_tract.loc[:, list_component_uniq].sum(axis=1)/len(np.unique(applicable_to_haz_df['Component Code'].tolist()))
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

    list_component_name_uniq = list(dict.fromkeys(resilience_df['RC Component'].values))
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














