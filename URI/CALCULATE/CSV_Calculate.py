""" produce CSV tables
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os


import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()
nan_value = 'NA'

def calculate_csv(list_abbrev_haz, list_geo, path_output):

     #%% loop through geographies
    list_geo_tot = ['CITYWIDE', 'BOROCODE', 'PUMA', 'NTA', 'BCT_txt']
    list_geo_folder_tot = ['Citywide', 'Borough', 'PUMA', 'NTA', 'Tract']
    dct_geo_folder = {list_geo_tot[x]: list_geo_folder_tot[x] for x in range(len(list_geo_tot))}
    list_geo_folder = [dct_geo_folder[x] for x in list_geo]

    df_csv = {}
    for (geo_id, geo_name) in zip(list_geo, list_geo_folder):

    # #%%
    #     geo_id = 'PUMA'
    #     geo_name = 'PUMA'
        print('Tabulating csv for {}'.format(geo_name))
        #loop through each uri hazard
        count = 0
        for haz in list_abbrev_haz:
            print('.', end='')
            path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\\{}\\URI_{}_{}.shp'.format(geo_name, haz, geo_name)
            gdf_haz = gpd.read_file(path_haz)
            if geo_id == 'CITYWIDE':gdf_haz['CITYWIDE'] = np.repeat(int(1), len(gdf_haz))

            #loop through each column and add based on title
            list_col_add = [col for col in gdf_haz.columns if haz in col[0:3]]
            for col in list_col_add:

                #%% add base to df_temp
                list_norm_keep = ['AREA_SQMI', 'FLOOR_SQFT', 'POP', 'BLD_CNT']
                list_col_keep = list_norm_keep + [col, geo_id]
                df = gdf_haz[list_col_keep].copy()

                df.rename(columns={geo_id:'GeoID', 'AREA_SQMI': 'Land_Area', 'FLOOR_SQFT':'Bldg_Area', 'POP':'Pop_2010',
                                            'BLD_CNT':'Bldg_Area', col:'Value'}, inplace=True)

                # add hazard
                list_hazards = ['CYB', 'EXH', 'WIW', 'CST', 'CER', 'HIW', 'ERQ', 'FLD', 'EMG', 'RES', 'CRN', 'ALL' ]
                list_names = ['Cyber Threat', 'Extreme Heat', 'Winter Weather', 'Coastal Storms', 'Coastal Erosion',
                              'High Winds', 'Earthquake', 'Flooding', 'Emerging Disease', 'Respiratory Illness',
                              'CBRN', 'All']
                dct_haz = {list_hazards[x]: list_names[x] for x in range(len(list_hazards))}
                label_hazard = dct_haz[col[0:3]]
                df['Hazard'] = np.repeat(label_hazard, len(df))


                #%% add Geography
                df['Geography'] = np.repeat(geo_name, len(df))

                # add component
                if col[3] == 'E':
                    if ((col[5]=='A') or (col[5]=='Q')):
                        label_Component = 'Absolute Expected Loss'
                    else:
                        label_Component = 'Expected Loss'
                elif col[3] == 'S':
                    label_Component = 'Social Vulnerability'
                elif col[3] == 'R':
                    label_Component = 'Resilience Capacity'
                elif col[3] == 'U':
                    if ((col[5]=='A') or (col[5]=='Q')):
                        label_Component = 'Absolute Risk Score'
                    else:
                        label_Component = 'Risk Score'
                else:
                    print("warning: no component label match")
                df['Component'] = np.repeat(label_Component, len(df))

                #%% add subcomponent

                list_rca_code = params.MITIGATION.loc[:, 'Component Code'].unique()
                list_rca_code_name = params.MITIGATION.loc[:, 'RC Component'].unique()
                dct_rca_subcomponent = {list_rca_code[x]: list_rca_code_name[x] for x in range(len(list_rca_code))}

                df_esl_subcomponents = params.CONSEQUENCES.copy()[['Sub_Components', 'Abbrv']].dropna()
                list_esl_code = df_esl_subcomponents.Abbrv.values
                list_esl_name = df_esl_subcomponents.Sub_Components.values
                dct_esl_subcomponent = {list_esl_code[x]: list_esl_name[x] for x in range(len(list_esl_code))}

                if ((label_Component=='Social Vulnerability') or ('Risk' in label_Component)):
                    label_SubComponent = ''
                elif col[3]=='R':
                    if col[6:8] == 'TT':
                        label_SubComponent = 'All'
                    else:
                        label_SubComponent = dct_rca_subcomponent[col[6:8]]
                elif col[3] == 'E':
                    if col[7:8] == 'T':
                        label_SubComponent = 'All'
                    else:
                        label_SubComponent = dct_esl_subcomponent[col[7:8]]
                else:
                    print("warning: no subcomponent match")
                df['Sub-Component'] = np.repeat(label_SubComponent, len(df))

                list_rca_factor_code = params.MITIGATION.loc[:, 'Factor Code'].unique()
                list_rca_factor_name = params.MITIGATION.loc[:, 'RC Factor'].unique()
                dct_rca_factor = {list_rca_factor_code[x]: list_rca_factor_name[x] for x in range(len(list_rca_factor_code))}

                if haz != 'ALL':
                    df_cons = params.CONSEQUENCES.copy()
                    # get columns for this hazard
                    haz_columns = [col for col in df_cons.columns if haz in col]
                    df_cons = df_cons[haz_columns]
                    list_esl_factor_code = df_cons[haz + '_Abbrv'].dropna().values
                    list_esl__factor_name = df_cons[haz + '_Factor'].dropna().values
                    dct_esl_factor = {list_esl_factor_code[x]: list_esl__factor_name[x] for x in range(len(list_esl_factor_code))}

                #%%add Factor
                if ((label_Component=='Social Vulnerability') or ('Risk' in label_Component)):
                    label_Factor = ''
                elif col[3]=='R':
                    if col[8:10] == 'TT':
                        label_Factor = 'All'
                    else:
                        label_Factor = dct_rca_factor[col[8:10]]
                elif col[3] == 'E':
                    if col[8:9] == 'T':
                        label_Factor = 'All'
                    else:
                        label_Factor = dct_esl_factor[col[8:9]]
                else:
                    print("warning: no subcomponent match")
                df['Factor'] = np.repeat(label_Factor, len(df))

                #%%add view
                list_view_code = ['R', 'S', 'P', 'A', 'Q']
                list_view_name = ['Raw Value', 'Score', 'Percentile', 'Score', 'Percentile']
                list_type_name_esl = ['2019 USD', '1-5 Value', 'Percent', '1-5 Value', 'Percent' ]
                list_type_name = ['Unitless', '1-5 Value', 'Percent', '1-5 Value', 'Percent' ]

                dct_view = {list_view_code[x]: list_view_name[x] for x in range(len(list_view_code))}
                dct_type = {list_view_code[x]: list_type_name[x] for x in range(len(list_view_code))}
                dct_type_esl = {list_view_code[x]: list_type_name_esl[x] for x in range(len(list_view_code))}

                if label_Component == 'Social Vulnerability':
                    label_view = dct_view[col[2]]
                    label_type = dct_type[col[2]]
                elif label_Component == 'Expected Loss':
                    label_view = dct_view[col[5]]
                    label_type = dct_type_esl[col[5]]
                else:
                    label_view = dct_view[col[5]]
                    label_type = dct_type[col[5]]
                df['View'] = np.repeat(label_view, len(df))
                df['Type'] = np.repeat(label_type, len(df))

                #%%add normalization
                list_norm_code = ['N', 'A', 'F', 'P']
                list_norm_name = ['None', 'Land Area', 'Building Area', 'Population']
                dct_norm = {list_norm_code[x]: list_norm_name[x] for x in range(len(list_norm_code))}

                if ((label_Component=='Social Vulnerability') or (label_Component=='Resilience Capacity')):
                    label_Norm = ''
                else:
                    label_Norm = dct_norm[col[6]]
                df['Normalization'] = np.repeat(label_Norm, len(df))
                if count == 0:
                    df_csv[geo_id] = df.copy()
                else:
                    df_csv[geo_id] =  df_csv[geo_id].append(df)
                count += 1

        df_csv[geo_id].replace(nan_value, np.nan, inplace=True)
        path_tracts = os.path.join(path_output, 'TBL_{}.csv'.format(geo_name))
        df_csv[geo_id].to_csv(path_tracts)
        print("")

    #%% combine
    for i, key in enumerate(df_csv.keys()):
        if i==0: df_master = df_csv[key].copy()
        else: df_master = df_master.append(df_csv[key])
    print('Saving master csv.')
    path_output = os.path.join(path_output, 'TBL_master.csv')
    df_master.to_csv(path_output)
    print('Done.')

#%%
if __name__ == '__main__':
    list_abbrev_haz = ['EXH', 'WIW']
    list_geo_tot = ['CITYWIDE', 'BOROCODE', 'PUMA', 'NTA', 'BCT_txt']
    path_output = r'C://temp//'
    calculate_csv(list_abbrev_haz, list_geo_tot, path_output)
