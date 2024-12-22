#calculate all URI and ESL values

#%% read packages
import geopandas as gpd
import URI.MISC.plotting_1 as plotting
import URI.MISC.utils_1 as utils
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES

utils.set_home()

def calculate_ALL(list_abbrev_haz):
    #%% open and merge all URI shapefiles
    for i, haz in enumerate(list_abbrev_haz):
        path_haz = PATHNAMES.OUTPUTS_folder + r'\URI\Tract\URI_{}_tract.shp'.format(haz, haz)
        if i==0:
            gdf_all = gpd.read_file(path_haz)
            len_check = len(gdf_all.columns)
        else:
            gdf_haz = gpd.read_file(path_haz)
            gdf_haz = gdf_haz.set_index('BCT_txt')
            list_col_keep = [col for col in gdf_haz.columns if haz in col]
            gdf_all = gdf_all.merge(gdf_haz[list_col_keep], left_on='BCT_txt', right_index=True, how='left')
            len_check += len(gdf_haz[list_col_keep].columns)

    #%% calculate ESL sum total all hazards
    list_col = [haz + 'E_RXXT' for haz in list_abbrev_haz]
    gdf_all['ALLE_RXXT'] = gdf_all[list_col].sum(axis=1)

    #%% cacluate all hazard average RCA
    list_col_RCA = [col for col in gdf_all.columns if 'R_RTTTT' in col]
    gdf_all['ALLR_RTTTT'] = gdf_all[list_col_RCA].mean(axis=1)

    #%% calcualte all hazard URI
    list_col_URI = [col for col in gdf_all.columns if 'U_RN' in col]
    gdf_all['ALLU_RN'] = gdf_all[list_col_URI].sum(axis=1)

    # %% calculate scores
    list_col = [col for col in gdf_all if 'ALL' in col]
    for col in list_col:
        score_col = col[0:5] + 'S' + col[6:]
        gdf_all = utils.calculate_kmeans(gdf_all, data_column=col, score_column=score_col)
        percentile_col = col[0:5] + 'P' + col[6:]
        gdf_all = utils.calculate_percentile(gdf_all, data_column=col, score_column=percentile_col)

    #%% plot results
    plotting.plot_notebook(gdf_all, column='ALLE_SXXT', title= 'All Hazard: Total Expected Loss',
                           legend='Score', cmap='Greens', type='score')
    plotting.plot_notebook(gdf_all, column='ALLR_STTTT', title= 'All Hazard: Total Resilience Capacity',
                           legend='Score', cmap='Blues', type='score')
    plotting.plot_notebook(gdf_all, column='ALLU_SN', title= 'All Hazard: Urban Risk Index',
                           legend='Score', cmap='Purples', type='score')


    #%% save
    list_col_keep = gdf_all.columns
    for haz in list_abbrev_haz:
        list_col_keep = [col for col in list_col_keep if haz not in col[0:3]]
    list_col_keep = ['BCT_txt', 'borocode', 'cdta2020', 'nta2020', 'geometry'] + [col for col in gdf_all.columns if (('ALL' in col) or ('S_' in col))]
    path_save = PATHNAMES.OUTPUTS_folder + r'\URI\Tract\URI_ALL_Tract.shp'
    gdf_all[list_col_keep].to_file(path_save)

