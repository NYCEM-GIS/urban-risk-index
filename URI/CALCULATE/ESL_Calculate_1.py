""" Calculate the total loss for each hazard"""

#%% read packages
import numpy as np
import geopandas as gpd
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()


#%% calculate ESL
def calculate_ESL(haz):
    print('Calculating {}'.format(haz))

    # open tract
    gdf_ESL = utils.get_blank_tract()

    #%%get factors, abbreviateions, path names
    #get lookup table for subcomponents
    df_sub = params.CONSEQUENCES.copy()[['Sub_Components', 'Abbrv']]
    df_sub.index = df_sub.Sub_Components

    # get list of consequences
    df_cons = params.CONSEQUENCES.copy()
    # get columns for this hazard
    haz_columns = [col for col in df_cons.columns if haz in col]
    df_cons = df_cons[haz_columns]
    df_cons.index = range(len(df_cons))
    df_cons.dropna(inplace=True, how='all', axis=0)

    print(".....Importing {} expected annual losses.....".format(haz))
    print(" ")
    list_subcomponents = []
    list_E_col = []
    for idx in df_cons.index:
        this_factor = df_cons.at[idx, '{}_Factor'.format(haz)]
        this_abbrv = df_cons.at[idx, '{}_Abbrv'.format(haz)]
        this_receptor = df_cons.at[idx, '{}_Receptor'.format(haz)]
        this_subcomponent = df_cons.at[idx, '{}_Subcomponent'.format(haz)]
        this_subcomponent_abbrv = df_sub.at[this_subcomponent, 'Abbrv']
        list_subcomponents.append(this_subcomponent_abbrv)
        this_path = df_cons.at[idx, '{}_Path_Name'.format(haz)]
        this_norm = 'N' #not normalized
        this_rank = 'R' #raw value
        print("..........Factor:  {}".format(this_factor))
        print("..........Abbreviation:  {}".format(this_abbrv))
        print("..........Receptor:  {}".format(this_receptor))
        print("..........Category:  {}".format(this_subcomponent))
        print(" ")
        # add consequence
        path_consequence = getattr(PATHNAMES, this_path)
        gdf_consequence = gpd.read_file(path_consequence)[['BCT_txt', 'Loss_USD']]
        this_name = haz + 'E_' + this_rank + this_norm + this_subcomponent_abbrv + this_abbrv
        gdf_consequence.rename(columns={"Loss_USD":this_name}, inplace=True)
        gdf_ESL = gdf_ESL.merge(gdf_consequence, on='BCT_txt', how='left')
        list_E_col.append(this_name)
        plotting.plot_notebook(gdf_ESL, column=this_name, title=haz + ': ' + this_factor,
                               legend='Loss USD', cmap='Greens', type='raw')
    # rename the columns in new Boundary tract file.    
    list_all_col = list_E_col.copy() + ['BCT_txt', 'geometry', 'borocode', 'nta2020', 'cdta2020']
    gdf_ESL = gdf_ESL[list_all_col]

    #%% get sum of subcompponents
    list_subcomponents = np.unique(list_subcomponents)
    for sub in list_subcomponents:
        list_col = [col for col in list_E_col if sub in col[7]]
        this_col = list_col[0][0:8] + 'T'
        gdf_ESL[this_col] = gdf_ESL[list_col].sum(axis=1)

    #%% get total sum
    this_col = haz + 'E_RNTT'
    gdf_ESL[this_col] = gdf_ESL[list_E_col].sum(axis=1)

    #%% add normalization factors
    path_norm = PATHNAMES.OTH_normalize_values
    df_norm = gpd.read_file(path_norm)
    df_norm.drop(columns={'geometry'}, inplace=True)
    gdf_ESL = gdf_ESL.merge(df_norm, on='BCT_txt', how='left')

    # Fill na wil 0 in gdf_ESL
    gdf_ESL = gdf_ESL.fillna(0)

    #%% calculate normalized values
    def divide_zero(x, y):
        if y==0 or y!=y or x!=x: # handling na and 0.
            return 0
        else:
            return x / y

    list_norm_col = ['AREA_SQMI', 'FLOOR_SQFT', 'POP']
    list_abbrv = ['A', 'F', 'P']
    for norm, abbrv in zip(list_norm_col, list_abbrv):
        list_col = [col for col in gdf_ESL if 'E_RN' in col]
        for col in list_col:
            new_col = col[0:6] + abbrv + col[7:]
            gdf_ESL[new_col] = gdf_ESL.apply(lambda row: divide_zero(row[col], row[norm]), axis=1)

    #%% calculate scores
    list_col = [col for col in gdf_ESL if 'E_R' in col]
    for col in list_col:
        score_col = col[0:5] + 'S' + col[6:]
        gdf_ESL = utils.calculate_kmeans(gdf_ESL, data_column=col, score_column=score_col)
        percentile_col = col[0:5] + 'P' + col[6:]
        gdf_ESL = utils.calculate_percentile(gdf_ESL, data_column=col, score_column=percentile_col)
    plotting.plot_notebook(gdf_ESL, column=haz + 'E_SNTT', title=haz + ': Total Loss',
                           legend='Score', cmap='Greens', type='score')


    #%%
    path_save = PATHNAMES.OUTPUTS_folder + r'\ESL\Tract\ESL_{}_Tract.shp'.format(haz, haz)
    gdf_ESL.to_file(path_save)


#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list and mitigation table
    folder_outputs = PATHNAMES.OUTPUTS_folder
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()

    #run script
    for haz in list_abbrev_haz[2:]:
        calculate_ESL(haz)


