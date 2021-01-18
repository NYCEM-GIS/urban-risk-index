""" make tableau files"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats

from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

nan_value = np.nan

#%% Create shapefile
#use URI_full, any hazard will work
haz='CST'
path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
    haz, haz)
gdf_shp = gpd.read_file(path_haz)
gdf_shp['Bldg_Area'] = gdf_shp['Floor_sqft'] / (5280.**2)
#save the most important fields
gdf_shp = gdf_shp[['BCT_txt', 'NEIGHBORHO', 'PUMA', 'BOROCODE', 'Sq_miles',
                   'Building_C', 'pop_2010', 'Bldg_Area', 'geometry']]
#add the borough names
path_bor = params.PATHNAMES.at['boroughs_table', 'Value']
df_bor = pd.read_excel(path_bor, index_col=0)
gdf_shp['Boro_Name'] = [df_bor.at[int(x), 'Name'] for x in gdf_shp['BOROCODE'].values]
#rename and reorder
gdf_shp.rename(columns={'BCT_txt': 'Census_Tract', 'NEIGHBORHO':'NTA_Name',
                        'BOROCODE':'Boro_Code', 'Sq_miles':'Land_Area',
                        'pop_2010':'Pop_2010', 'Building_C':'Bldg_Count'}, inplace=True)
gdf_shp = gdf_shp[['Census_Tract', 'NTA_Name', 'PUMA', 'Boro_Code', 'Boro_Name',
                   'Land_Area', 'Pop_2010', 'Bldg_Count', 'Bldg_Area', 'geometry']]
path_shp = params.PATHNAMES.at['TBL_shp', 'Value']
gdf_shp.to_file(path_shp)

#%% Create census tract summmary for tableau - first addition

path_results = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\\SOV\SOV_tract.shp'
gdf_SOV = gpd.read_file(path_results)
df_tract = gdf_SOV[['BCT_txt','SOV']].merge(gdf_shp[['Census_Tract', 'NTA_Name', 'PUMA', 'Boro_Code', 'Boro_Name',
                   'Land_Area', 'Pop_2010', 'Bldg_Count', 'Bldg_Area']], left_on='BCT_txt',
                                          right_on='Census_Tract', how='left')
df_tract.drop(columns=['BCT_txt'], inplace=True)
df_tract.rename(columns={'SOV':'Value'}, inplace=True)
df_tract['Geography'] = np.repeat('Tract', len(df_tract))
df_tract['Hazard'] = np.repeat('All', len(df_tract))
df_tract['Component'] = np.repeat('Social Vulnerabilty', len(df_tract))
df_tract['Sub-Component'] = np.repeat(nan_value, len(df_tract))
df_tract['Factor'] = np.repeat(nan_value, len(df_tract))
df_tract['View'] = np.repeat('Score', len(df_tract))
df_tract['Type'] = np.repeat("1-5 Value", len(df_tract))
df_tract['Normalization'] = np.repeat(nan_value, len(df_tract))

#%% write function to update

def update_tract(df_master, df_base, df_new, value_column, hazard=np.nan, component=np.nan,
                 subcomponent=np.nan, factor=np.nan, view=np.nan, view_type=np.nan, normalization=np.nan,
                 base_key='Census_Tract', new_key='BCT_txt'):
    df = df_new[[new_key, value_column]].merge(df_base[['Census_Tract', 'NTA_Name', 'PUMA', 'Boro_Code', 'Boro_Name',
                   'Land_Area', 'Pop_2010', 'Bldg_Count', 'Bldg_Area']], left_on=new_key, right_on=base_key, how='left')
    df.drop(columns=[new_key], inplace=True)
    df.rename(columns={value_column: 'Value'}, inplace=True)
    df['Geography'] = np.repeat('Tract', len(df))
    df['Hazard'] = np.repeat(hazard, len(df))
    df['Component'] = np.repeat(component, len(df))
    df['Sub-Component'] = np.repeat(subcomponent, len(df))
    df['Factor'] = np.repeat(factor, len(df))
    df['View'] = np.repeat(view, len(df))
    df['Type'] = np.repeat(view_type, len(df))
    df['Normalization'] = np.repeat(normalization, len(df))
    df_updated = df_master.append(df)
    return df_updated


#%% add SOV percentile
gdf_SOV['percent_score'] = np.round([stats.percentileofscore(gdf_SOV['SOV'].values, x, kind='rank') for x in gdf_SOV['SOV'].values], 2)
df_tract = update_tract(df_tract, gdf_shp, gdf_SOV, value_column='percent_score', component='Social Vulnerability',
                        hazard='All', view='Percentile', view_type='Percent')

#%% add resilience capacity all and four subcomponents (hazards specific)
list_hazards = ['EXH', 'WIW']#, 'CST', 'CER', 'HIW', 'ERQ', 'FLD', 'EMG', 'RES', 'CRN', ]
list_names = ['Extreme Heat', 'Winter Weather']#, 'Coastal Storms', 'Coastal Erosion',
              #'High Winds', 'Earthquake', 'Flooding', 'Emerging Disease', 'Respiratory Illness',
              #'CBRN']
list_value_column = ['RCA', 'CC', 'ML', 'RC', 'RR']
list_subcomponent = ['All', 'Community Capital', 'Mitigation Landscape', 'Response Capacity', 'Recovery Resources']
list_view = ['Score', 'Percentile']
list_view_type = ['1-5 Value', 'Percent']

#add all and subcomponent scores
for i in np.arange(len(list_hazards)):
    haz = list_hazards[i]
    haz_name = list_names[i]
    path_RCA =  params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\\RCA\\RCA_{}_tract.shp'.format(haz)
    gdf_RCA = gpd.read_file(path_RCA)
    for j, value_column_raw in enumerate(list_value_column):
        gdf_RCA[value_column_raw + '_percent'] = np.round([stats.percentileofscore(gdf_RCA[value_column_raw].values, x, kind='rank') for x in gdf_RCA[value_column_raw].values], 2)
        subcomponent = list_subcomponent[j]
        component = 'Resilience Capacity'
        for k, view in enumerate(list_view):
            view_type = list_view_type[k]
            if view=='Score':
                value_column = value_column_raw
            else:
                value_column = value_column_raw + '_percent'
            df_tract = update_tract(df_tract, gdf_shp, gdf_RCA, value_column=value_column,
                                    hazard = haz_name, component=component,
                                    subcomponent = subcomponent, factor='All',
                                    view=view, view_type=view_type)

    #%% add mitigation factors
    #loop through list of mitigation factors
    for idx in params.MITIGATION.index:
        this_bool = params.MITIGATION.at[idx, haz]
        if this_bool == 1:
            this_factor = params.MITIGATION.at[idx, 'RC Factor']
            this_factor_code = params.MITIGATION.at[idx, 'Factor Code']
            this_component_code = params.MITIGATION.at[idx, 'Component Code']
            this_component_name = params.MITIGATION.at[idx, 'RC Component']
            value_column_raw = this_component_code + '_' + this_factor_code
            gdf_RCA[value_column_raw + '_percent'] = np.round([stats.percentileofscore(gdf_RCA[value_column_raw].values, x, kind='rank') for x in gdf_RCA[value_column_raw].values], 2)
            for k, view in enumerate(list_view):
                view_type = list_view_type[k]
                if view == 'Score':
                    value_column = value_column_raw
                else:
                    value_column = value_column_raw + '_percent'
                df_tract = update_tract(df_tract, gdf_shp, gdf_RCA, value_column=value_column,
                                        hazard=haz_name, component=component,
                                        subcomponent=this_component_name, factor=this_factor,
                                        view=view, view_type=view_type)

#%% add ESL

#%% save file
path_tracts = r'C:\temp\df_tract.csv' #params.PATHNAMES.at['TBL_tracts', "Value"]
df_tract.to_csv(path_tracts)
