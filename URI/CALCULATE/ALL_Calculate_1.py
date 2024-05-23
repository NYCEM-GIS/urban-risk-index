#calculate all URI and ESL values

#%% read packages
import geopandas as gpd
import URI.MISC.params_1 as params
import URI.MISC.plotting_1 as plotting
import URI.MISC.utils_1 as utils

utils.set_home()

def calculate_ALL(list_abbrev_haz):
    #%% open and merge all URI shapefiles
    for i, haz in enumerate(list_abbrev_haz):
        print(haz)
        path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_{}_tract.shp'.format(haz, haz)
        if i==0:
            gdf_all = gpd.read_file(path_haz)
            len_check = len(gdf_all.columns)
        else:
            gdf_haz = gpd.read_file(path_haz)
            list_col_keep = [col for col in gdf_haz.columns if haz in col]
            list_col_keep.append('BCT_txt')
            gdf_all = gdf_all.merge(gdf_haz[list_col_keep], on='BCT_txt', how='left')
            len_check += len(gdf_haz[list_col_keep].columns)

    #%% calculate ESL sum total all hazards
    list_col = [haz + 'E_RNTT' for haz in list_abbrev_haz]
    gdf_all['ALLE_RNTT'] = gdf_all[list_col].sum(axis=1)

    #%% cacluate all hazard average RCA
    list_col_RCA = [col for col in gdf_all.columns if 'R_RTTTT' in col]
    gdf_all['ALLR_RTTTT'] = gdf_all[list_col_RCA].mean(axis=1)

    #%% calcualte all hazard URI
    list_col_URI = [col for col in gdf_all.columns if 'U_RN' in col]
    gdf_all['ALLU_RN'] = gdf_all[list_col_URI].sum(axis=1)

    #%% remove duplicate losses (e.g., high winds)
    x=0
    for i, haz in enumerate(list_abbrev_haz):
        df_sub = params.CONSEQUENCES.copy()[['Sub_Components', 'Abbrv']]
        df_sub.index = df_sub.Sub_Components
        df_cons = params.CONSEQUENCES.copy()
        # get columns for this hazard
        haz_columns = [col for col in df_cons.columns if haz in col]
        df_cons = df_cons[haz_columns]
        df_cons.index = range(len(df_cons))
        df_cons.dropna(inplace=True, how='all', axis=0)
        for idx in df_cons.index:
            this_duplicate =  df_cons.at[idx, '{}_Duplicate'.format(haz)]
            if this_duplicate.lower() == 'yes':
                this_factor = df_cons.at[idx, '{}_Factor'.format(haz)]
                this_abbrv = df_cons.at[idx, '{}_Abbrv'.format(haz)]
                this_subcomponent = df_cons.at[idx, '{}_Subcomponent'.format(haz)]
                this_subcomponent_abbrv = df_sub.at[this_subcomponent, 'Abbrv']
                esl_loss = gdf_all[haz+'E_RN'+this_subcomponent_abbrv+ this_abbrv].copy()
                uri_loss = esl_loss * gdf_all['S_R'] / gdf_all[haz+'R_RTTTT']
                gdf_all['ALLE_RNTT'] =  gdf_all['ALLE_RNTT']  - esl_loss
                gdf_all['ALLU_RN'] = gdf_all['ALLU_RN']  - uri_loss
                #print("Deleted duplicate loss {} for hazard {} worth {}".format(this_factor, haz, esl_loss.sum()))

    #%% calculate normalized values
    list_norm_col = ['AREA_SQMI', 'FLOOR_SQFT', 'POP']
    list_abbrv = ['A', 'F', 'P']
    list_col = [col for col in gdf_all.columns if (('ALLE_RN' in col) or ('ALLU_RN' in col))]
    for norm, abbrv in zip(list_norm_col, list_abbrv):
        for col in list_col:
            new_col = col[0:6] + abbrv + col[7:]
            gdf_all[new_col] = gdf_all.apply(lambda row: utils.divide_zero(row[col], row[norm]), axis=1)

    # %% calculate scores
    list_col = [col for col in gdf_all if 'ALL' in col]
    for col in list_col:
        score_col = col[0:5] + 'S' + col[6:]
        gdf_all = utils.calculate_kmeans(gdf_all, data_column=col, score_column=score_col)
        percentile_col = col[0:5] + 'P' + col[6:]
        gdf_all = utils.calculate_percentile(gdf_all, data_column=col, score_column=percentile_col)

    #%% plot results
    plotting.plot_notebook(gdf_all, column='ALLE_SNTT', title= 'All Hazard: Total Expected Loss',
                           legend='Score', cmap='Greens', type='score')
    plotting.plot_notebook(gdf_all, column='ALLR_STTTT', title= 'All Hazard: Total Resilience Capacity',
                           legend='Score', cmap='Blues', type='score')
    plotting.plot_notebook(gdf_all, column='ALLU_SN', title= 'All Hazard: Urban Risk Index',
                           legend='Score', cmap='Purples', type='score')

    #%% save
    list_col_keep = gdf_all.columns
    for haz in list_abbrev_haz:
        list_col_keep = [col for col in list_col_keep if haz not in col[0:3]]
    list_col_keep = list_norm_col + ['BCT_txt', 'borocode', 'cdta2020', 'nta2020', 'geometry', 'BLD_CNT'] + [col for col in gdf_all.columns if (('ALL' in col) or ('S_' in col))]
    path_save = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\Tract\URI_ALL_Tract.shp'
    gdf_all[list_col_keep].to_file(path_save)


#%% main
if __name__ == '__main__':

    # %% open outputs path and get abbrev list
    folder_outputs = params.PATHNAMES.at['OUTPUTS_folder', 'Value']
    list_abbrev_haz = params.ABBREVIATIONS.iloc[0:11, 0].values.tolist()
    list_abbrev_haz.remove('CYB')

    #run script
    calculate_ALL(list_abbrev_haz[0:2])







