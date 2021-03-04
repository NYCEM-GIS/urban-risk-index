""" make tableau files"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import scipy.stats as stats

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

nan_value = 'NA'

#%% Create shapefile
#use URI_full, any hazard will work
haz='CST'
path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
    haz, haz)
gdf_shp = gpd.read_file(path_haz)
gdf_shp['Bldg_Area'] = gdf_shp['Floor_sqft']
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
gdf_tract = gdf_shp.copy()

#aggregate date first
df_data= gdf_shp.groupby(["NTA_Name"]).agg(Pop_2010=("Pop_2010", sum),
                                             Bldg_Count=("Bldg_Count", sum),
                                             Bldg_Area=("Bldg_Area", sum),
                                             Land_Area=("Land_Area", sum))
#dissolve the geometry
gdf_shp  = gdf_shp.dissolve(by='NTA_Name')
gdf_shp = gdf_shp[['geometry']].merge(df_data, left_index=True, right_on='NTA_Name', how='left')
gdf_shp['NTA_Name'] = gdf_shp.index
gdf_shp.index.name = 'Index'
path_shp = params.PATHNAMES.at['TBL_N_shp', 'Value']
gdf_shp.to_file(path_shp)

#%% Create census tract summmary for tableau - first addition

path_results = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\\SOV\SOV_tract.shp'
gdf_SOV = gpd.read_file(path_results)
gdf_SOV = gdf_SOV.merge(gdf_tract[['Census_Tract', 'NTA_Name', 'Pop_2010']], left_on='BCT_txt', right_on='Census_Tract', how='left')

def weight_ave(x, weights):
    if weights.sum() != 0:
        result = np.average(x, weights=weights)
    else:
        result = 3
    return result

wm = lambda x: weight_ave(x, weights=gdf_SOV.loc[x.index, "Pop_2010"])
# run for neighborhoods
gdf_SOV = gdf_SOV.groupby(["NTA_Name"]).agg(SOV=("SOV", wm))
gdf_SOV['NTA_Name'] = gdf_SOV.index
gdf_SOV.index.name = 'Index'
df_tract = gdf_SOV[['NTA_Name','SOV']].merge(gdf_shp[[ 'NTA_Name',
                   'Land_Area', 'Pop_2010', 'Bldg_Count', 'Bldg_Area']], left_on='NTA_Name',
                                          right_on='NTA_Name', how='left')
df_tract.rename(columns={'SOV':'Value'}, inplace=True)
df_tract['Geography'] = np.repeat('NTA', len(df_tract))
df_tract['Hazard'] = np.repeat('All', len(df_tract))
df_tract['Component'] = np.repeat('Social Vulnerability', len(df_tract))
df_tract['Sub-Component'] = np.repeat(nan_value, len(df_tract))
df_tract['Factor'] = np.repeat(nan_value, len(df_tract))
df_tract['View'] = np.repeat('Raw Value', len(df_tract))
df_tract['Type'] = np.repeat("Unitless", len(df_tract))
df_tract['Normalization'] = np.repeat(nan_value, len(df_tract))

#%% write function to update

def update_tract(df_master, df_base, df_new, value_column, hazard=nan_value, component=nan_value,
                 subcomponent=nan_value, factor=nan_value, view=nan_value, view_type=nan_value, normalization=nan_value,
                 base_key='NTA_Name', new_key='NTA_Name'):
    df = df_new[[new_key, value_column]].merge(df_base[['NTA_Name',
                   'Land_Area', 'Pop_2010', 'Bldg_Count', 'Bldg_Area']], left_on=new_key, right_on=base_key, how='left')
    #df.drop(columns=[new_key], inplace=True)
    df.rename(columns={value_column: 'Value'}, inplace=True)
    df['Geography'] = np.repeat('NTA', len(df))
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

#add SOV score
gdf_SOV['1_5_score'] = [int(np.round(x,0)) for x in gdf_SOV['SOV'].values]
df_tract = update_tract(df_tract, gdf_shp, gdf_SOV, value_column='1_5_score', component='Social Vulnerability',
                        hazard='All', view='Score', view_type='1-5 Value')

#%% add resilience capacity all and four subcomponents (hazards specific)
list_hazards = ['EXH', 'WIW','CST', 'CER', 'HIW', 'ERQ', 'FLD', 'EMG', 'RES', 'CRN', ]
list_names = ['Extreme Heat', 'Winter Weather', 'Coastal Storms', 'Coastal Erosion', 'High Winds', 'Earthquake', 'Flooding', 'Emerging Disease', 'Respiratory Illness', 'CBRN']
list_value_column = ['RCA', 'CC', 'ML', 'RC', 'RR']
list_subcomponent = ['All', 'Community Capital', 'Mitigation Landscape', 'Response Capacity', 'Recovery Resources']
list_view = ['Raw Value', 'Score', 'Percentile']
list_view_type = ['Unitless', '1-5 Value', 'Percent']

#add all and subcomponent scores
for i in np.arange(len(list_hazards)):
    haz = list_hazards[i]
    haz_name = list_names[i]
    path_RCA =  params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\\RCA\\RCA_{}_tract.shp'.format(haz)
    gdf_RCA = gpd.read_file(path_RCA)
    gdf_RCA = gdf_RCA.merge(gdf_tract[['NTA_Name', 'Pop_2010', 'Census_Tract']], left_on='BCT_txt', right_on='Census_Tract', how='left')
    wm = lambda x: weight_ave(x, weights=gdf_RCA.loc[x.index, "Pop_2010"])
    gdf_RCA  = gdf_RCA.groupby(["NTA_Name"]).agg(wm)
    gdf_RCA.index.name = 'Index'
    gdf_RCA['NTA_Name'] = gdf_RCA.index
    for j, value_column_raw in enumerate(list_value_column):
        gdf_RCA[value_column_raw + '_percent'] = np.round([stats.percentileofscore(gdf_RCA[value_column_raw].values, x, kind='rank') for x in np.round(gdf_RCA[value_column_raw].values, 6)], 2)
        gdf_RCA[value_column_raw + '_score'] = [int(np.round(x,0)) for x in gdf_RCA[value_column_raw].values]
        subcomponent = list_subcomponent[j]
        component = 'Resilience Capacity'
        for k, view in enumerate(list_view):
            view_type = list_view_type[k]
            if view=='Raw Value':
                value_column = value_column_raw
            elif view=='Score':
                value_column = value_column_raw + '_score'
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
            gdf_RCA[value_column_raw + '_percent'] = np.round([stats.percentileofscore(gdf_RCA[value_column_raw].values, x, kind='rank') for x in np.round(gdf_RCA[value_column_raw].values, 6)], 2)
            gdf_RCA[value_column_raw + '_score'] = [int(np.round(x,0)) for x in gdf_RCA[value_column_raw].values]
            for k, view in enumerate(list_view):
                view_type = list_view_type[k]
                if view == 'Raw Value':
                    value_column = value_column_raw
                elif view == 'Score':
                    value_column = value_column_raw + '_score'
                else:
                    value_column = value_column_raw + '_percent'
                df_tract = update_tract(df_tract, gdf_shp, gdf_RCA, value_column=value_column,
                                        hazard=haz_name, component=component,
                                        subcomponent=this_component_name, factor=this_factor,
                                        view=view, view_type=view_type)

#%% add ESL factors

def divide_zero(x, y):
    if y==0:
        return 0
    else:
        return x / y


list_norm = ['None', 'Population', 'Building Area', 'Land Area']
list_score = ['Raw Value', 'Score', 'Percentile']
for i in np.arange(len(list_hazards)):
    haz = list_hazards[i]
    haz_name = list_names[i]
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(haz, haz)
    gdf_uri = gpd.read_file(path_haz)
    gdf_uri['NTA_Name'] = gdf_uri['NEIGHBORHO']
    wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    gdf_temp = gdf_uri.groupby(["NTA_Name"]).agg(wm)
    gdf_uri = gdf_uri.groupby(["NEIGHBORHO"]).agg(sum)
    gdf_uri['NTA_Name'] = gdf_uri.index
    gdf_uri.index=np.arange(len(gdf_uri))
    #wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    #gdf_temp = gdf_uri.groupby(["Boro_Code"]).agg(wm)
    #drop SOV, RCA, add previously aggregated values
    gdf_uri.drop(columns=['SOV', 'RCA'], inplace=True)
    #add back in
    gdf_uri = gdf_uri.merge(gdf_temp[['SOV','RCA']], left_on='NTA_Name', right_index=True, how='left')
    df_cons = params.CONSEQUENCES.copy()
    #get columns for this hazard
    haz_columns = [col for col in df_cons.columns if haz in col]
    df_cons = df_cons[haz_columns]
    df_cons.index = range(len(df_cons))
    df_cons.dropna(inplace=True)

    #loop through each factor and add
    for idx in df_cons.index:
        this_factor = df_cons.at[idx, '{}_Factor'.format(haz)]
        this_receptor = df_cons.at[idx, '{}_Receptor'.format(haz)]
        this_subcomponent = df_cons.at[idx, '{}_Subcomponent'.format(haz)]
        value_column = ('ESL_' + this_factor.replace(" ", "_"))[:10]
        #no normalization
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column,score_column=value_column + "_score")
        gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in np.round(gdf_uri[value_column].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'None')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'None')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'None')
        #normalize by popultion
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'pop_2010']) for x in gdf_uri.index]
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Population')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Population')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Population')
        #normalize by building
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Floor_sqft']) for x in gdf_uri.index]
        gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Building Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Building Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Building Area')
        #normalize by area
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Sq_miles']) for x in gdf_uri.index]
        gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Land Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Land Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Land Area')

    #%% calculate ESL for subcomponents
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(haz, haz)
    gdf_uri = gpd.read_file(path_haz)
    gdf_uri['NTA_Name'] = gdf_uri['NEIGHBORHO']
    wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    gdf_temp = gdf_uri.groupby(["NTA_Name"]).agg(wm)
    gdf_uri = gdf_uri.groupby(["NEIGHBORHO"]).agg(sum)
    gdf_uri['NTA_Name'] = gdf_uri.index
    gdf_uri.index=np.arange(len(gdf_uri))
    #wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    #gdf_temp = gdf_uri.groupby(["Boro_Code"]).agg(wm)
    #drop SOV, RCA, add previously aggregated values
    gdf_uri.drop(columns=['SOV', 'RCA'], inplace=True)
    #add back in
    gdf_uri = gdf_uri.merge(gdf_temp[['SOV','RCA']], left_on='NTA_Name', right_index=True, how='left')
    df_cons = params.CONSEQUENCES.copy()
    #get columns for this hazard
    haz_columns = [col for col in df_cons.columns if haz in col]
    df_cons = df_cons[haz_columns]
    df_cons.index = range(len(df_cons))
    df_cons.dropna(inplace=True)
    list_subcomponents = df_cons['{}_Subcomponent'.format(haz)].unique()

    #loop through each factor and add
    for sub in list_subcomponents:
        df_sub = df_cons.loc[df_cons['{}_Subcomponent'.format(haz)]==sub, :]
        list_value_columns = [('ESL_' + x.replace(" ", "_"))[:10] for x in df_sub['{}_Factor'.format(haz)]]
        this_factor = 'All'
        this_subcomponent = sub
        value_column = 'ESL_' + sub.replace(' ', '_')
        gdf_uri[value_column] = gdf_uri[list_value_columns].sum(axis=1)
        #no normalization
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column,score_column=value_column + "_score")
        gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in np.round(gdf_uri[value_column].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'None')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'None')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'None')
        #normalize by popultion
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'pop_2010']) for x in gdf_uri.index]
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Population')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Population')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Population')
        #normalize by building
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Floor_sqft']) for x in gdf_uri.index]
        gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Building Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Building Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Building Area')
        #normalize by area
        gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Sq_miles']) for x in gdf_uri.index]
        gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
        gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
        gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Raw Value', view_type='2019 USD', normalization = 'Land Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Score', view_type='1-5 Value', normalization = 'Land Area')
        df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                                hazard = haz_name, component='Expected Loss',
                                subcomponent = this_subcomponent, factor=this_factor,
                                view='Percentile', view_type='Percent', normalization = 'Land Area')

    #%% calculate ESL for subcomponents
    path_haz = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(haz, haz)
    gdf_uri = gpd.read_file(path_haz)
    gdf_uri['NTA_Name'] = gdf_uri['NEIGHBORHO']
    wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    gdf_temp = gdf_uri.groupby(["NTA_Name"]).agg(wm)
    gdf_uri = gdf_uri.groupby(["NEIGHBORHO"]).agg(sum)
    gdf_uri['NTA_Name'] = gdf_uri.index
    gdf_uri.index=np.arange(len(gdf_uri))
    #wm = lambda x: weight_ave(x, weights=gdf_uri.loc[x.index, "pop_2010"])
    #gdf_temp = gdf_uri.groupby(["Boro_Code"]).agg(wm)
    #drop SOV, RCA, add previously aggregated values
    gdf_uri.drop(columns=['SOV', 'RCA'], inplace=True)
    #add back in
    gdf_uri = gdf_uri.merge(gdf_temp[['SOV','RCA']], left_on='NTA_Name', right_index=True, how='left')
    value_column = 'ESL'
    this_subcomponent = 'All'
    this_factor ='All'
    #no normalization
    gdf_uri= utils.calculate_kmeans(gdf_uri, value_column,score_column=value_column + "_score")
    gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in np.round(gdf_uri[value_column].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Raw Value', view_type='2019 USD', normalization = 'None')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Score', view_type='1-5 Value', normalization = 'None')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Percentile', view_type='Percent', normalization = 'None')
    #calculate URI
    value_column = 'URI_raw'
    gdf_uri['URI_raw'] = gdf_uri['ESL'] * gdf_uri['SOV'] / gdf_uri['RCA']
    gdf_uri = utils.calculate_kmeans(gdf_uri, value_column, score_column=value_column + "_score")
    gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in np.round(gdf_uri[value_column].values, 6)],2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                            hazard = haz_name, component='Risk Score',
                            view='Raw Value', view_type='2019 USD', normalization = 'None')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                            hazard = haz_name, component='Risk Score',
                            view='Score', view_type='1-5 Value', normalization = 'None')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                            hazard = haz_name, component='Risk Score',
                            view='Percentile', view_type='Percent', normalization = 'None')


    #normalize by popultion
    value_column = 'ESL'
    gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'pop_2010']) for x in gdf_uri.index]
    gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
    gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Raw Value', view_type='2019 USD', normalization = 'Population')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Score', view_type='1-5 Value', normalization = 'Population')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Percentile', view_type='Percent', normalization = 'Population')
    #calculate URI
    value_column = 'URI_raw_norm'
    gdf_uri[value_column] = gdf_uri['ESL_norm'] * gdf_uri['SOV'] / gdf_uri['RCA']
    gdf_uri = utils.calculate_kmeans(gdf_uri, value_column, score_column=value_column + "_score")
    gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in gdf_uri[value_column].values],2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                            hazard = haz_name, component='Risk Score',
                            view='Raw Value', view_type='2019 USD', normalization = 'Population')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                            hazard = haz_name, component='Risk Score',
                            view='Score', view_type='1-5 Value', normalization = 'Population')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                            hazard = haz_name, component='Risk Score',
                            view='Percentile', view_type='Percent', normalization = 'Population')

    #normalize by building
    value_column = 'ESL'
    gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Floor_sqft']) for x in gdf_uri.index]
    gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
    gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
    gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Raw Value', view_type='2019 USD', normalization = 'Building Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Score', view_type='1-5 Value', normalization = 'Building Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Percentile', view_type='Percent', normalization = 'Building Area')
    #calculate URI
    value_column = 'URI_raw_norm'
    gdf_uri[value_column] = gdf_uri['ESL_norm'] * gdf_uri['SOV'] / gdf_uri['RCA']
    gdf_uri.drop(columns=value_column + "_score", inplace=True)
    gdf_uri = utils.calculate_kmeans(gdf_uri, value_column, score_column=value_column + "_score")
    gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in np.round(gdf_uri[value_column].values, 6)],2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                            hazard = haz_name, component='Risk Score',
                            view='Raw Value', view_type='2019 USD', normalization = 'Building Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                            hazard = haz_name, component='Risk Score',
                            view='Score', view_type='1-5 Value', normalization = 'Building Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                            hazard = haz_name, component='Risk Score',
                            view='Percentile', view_type='Percent', normalization = 'Building Area')

    #normalize by area
    value_column = 'ESL'
    gdf_uri[value_column + '_norm'] = [divide_zero(gdf_uri.at[x, value_column], gdf_uri.at[x, 'Sq_miles']) for x in gdf_uri.index]
    gdf_uri.drop(columns=value_column + "_norm_score", inplace=True)
    gdf_uri= utils.calculate_kmeans(gdf_uri, value_column + '_norm',score_column=value_column + "_norm_score")
    gdf_uri[value_column + '_norm_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column + '_norm'].values, x, kind='rank') for x in np.round(gdf_uri[value_column + '_norm'].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Raw Value', view_type='2019 USD', normalization = 'Land Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_score",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Score', view_type='1-5 Value', normalization = 'Land Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_norm_percent",
                            hazard = haz_name, component='Expected Loss',
                            subcomponent = this_subcomponent, factor=this_factor,
                            view='Percentile', view_type='Percent', normalization = 'Land Area')
    #calculate URI
    value_column = 'URI_raw_norm'
    gdf_uri[value_column] = gdf_uri['ESL_norm'] * gdf_uri['SOV'] / gdf_uri['RCA']
    gdf_uri.drop(columns=value_column + "_score", inplace=True)
    gdf_uri = utils.calculate_kmeans(gdf_uri, value_column, score_column=value_column + "_score")
    gdf_uri[value_column + '_percent'] = np.round([stats.percentileofscore(gdf_uri[value_column].values, x, kind='rank') for x in gdf_uri[value_column].values],2)
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column,
                            hazard = haz_name, component='Risk Score',
                            view='Raw Value', view_type='2019 USD', normalization = 'Land Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_score",
                            hazard = haz_name, component='Risk Score',
                            view='Score', view_type='1-5 Value', normalization = 'Land Area')
    df_tract = update_tract(df_tract, gdf_shp, gdf_uri, value_column=value_column + "_percent",
                            hazard = haz_name, component='Risk Score',
                            view='Percentile', view_type='Percent', normalization = 'Land Area')

#%% calculate absolute URI
#get raw values of risk score
list_norm = ['None', 'Population', 'Building Area', 'Land Area']
for norm in list_norm:
    value_column='Value'
    df_uri = df_tract.loc[(df_tract.Component == 'Risk Score') & (df_tract.Normalization == norm) & (df_tract.View=='Raw Value'), :].copy()
    df_uri = utils.calculate_kmeans(df_uri, value_column, score_column="URI_abs_score")
    df_uri['URI_abs_percent'] = np.round([stats.percentileofscore(df_uri[value_column].values, x, kind='rank') for x in np.round(df_uri[value_column].values, 6)],2)
    #add tract for each hazard
    for haz in list_names:
        this_uri = df_uri.loc[df_uri.Hazard==haz, :].copy()
        #this_uri['BCT_txt'] = this_uri['Census_Tract'].copy()
        df_tract = update_tract(df_tract, gdf_shp, this_uri, value_column="URI_abs_score",
                                hazard = haz, component='Risk Score Absolute',
                                view='Score', view_type='1-5 Value', normalization = norm)
        df_tract = update_tract(df_tract, gdf_shp, this_uri, value_column="URI_abs_percent",
                                hazard = haz, component='Risk Score Absolute',
                                view='Percentile', view_type='Percent', normalization = norm)

#%% calculate all URI
#get all values of risk score
list_norm = ['None', 'Population', 'Building Area', 'Land Area']
for norm in list_norm:
    value_column='Value'
    df_uri = df_tract.loc[(df_tract.Component == 'Risk Score') & (df_tract.Normalization == norm) & (df_tract.View=='Raw Value') & \
            (df_tract.Hazard != 'High Wind') & (df_tract.Hazard != 'Flooding'), :].copy()
    df_all = df_uri[['Value', 'NTA_Name']].groupby(by='NTA_Name').sum()
    df_all['NTA_Name'] = df_all.index
    df_all = utils.calculate_kmeans(df_all, value_column, score_column="URI_all_score")
    df_all['URI_all_percent'] = np.round([stats.percentileofscore(df_all[value_column].values, x, kind='rank') for x in
                                          np.round(df_all[value_column].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="Value",
                            hazard='All', component='Risk Score',
                            view='Raw Value', view_type='2019 USD', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="URI_all_score",
                            hazard='All', component='Risk Score',
                            view='Score', view_type='1-5 Value', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="URI_all_percent",
                            hazard='All', component='Risk Score',
                            view='Percentile', view_type='Percent', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')

#get all values of ESL
list_norm = ['None', 'Population', 'Building Area', 'Land Area']
for norm in list_norm:
    value_column='Value'
    df_uri = df_tract.loc[(df_tract.Component == 'Expected Loss') & (df_tract.Normalization == norm) & (df_tract.View=='Raw Value') & \
                          (df_tract.Factor=='All') & (df_tract['Sub-Component']=='All') & \
                          (df_tract.Hazard != 'High Wind') & (df_tract.Hazard != 'Flooding'), :].copy()
    df_all = df_uri[['Value', 'NTA_Name']].groupby(by='NTA_Name').sum()
    df_all['NTA_Name'] = df_all.index
    df_all = utils.calculate_kmeans(df_all, value_column, score_column="ESL_all_score")
    df_all['ESL_all_percent'] = np.round([stats.percentileofscore(df_all[value_column].values, x, kind='rank') for x in
                                          np.round(df_all[value_column].values, 6)], 2)
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="Value",
                            hazard='All', component='Expected Loss',
                            subcomponent='All', factor='All',
                            view='Raw Value', view_type='2019 USD', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="ESL_all_score",
                            hazard='All', component='Expected Loss',
                            subcomponent='All', factor='All',
                            view='Score', view_type='1-5 Value', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')
    df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="ESL_all_percent",
                            hazard='All', component='Expected Loss',
                            subcomponent='All', factor='All',
                            view='Percentile', view_type='Percent', normalization=norm,
                            base_key='NTA_Name', new_key='NTA_Name')

#repeat all subcomponents
list_sub = ['Mortality Loss', 'Morbidity Loss', 'Property Loss', 'Environmental Loss',  'Response Cost', 'Indirect Cost']
list_norm = ['None', 'Population', 'Building Area', 'Land Area']
for sub in list_sub:
    for norm in list_norm:
        value_column='Value'
        df_uri = df_tract.loc[(df_tract.Component == 'Expected Loss') & (df_tract.Normalization == norm) & (df_tract.View=='Raw Value') & \
                              (df_tract.Factor=='All') & (df_tract['Sub-Component']==sub) & \
                              (df_tract.Hazard != 'High Wind') & (df_tract.Hazard != 'Flooding'), :].copy()
        df_all = df_uri[['Value', 'NTA_Name']].groupby(by='NTA_Name').sum()
        df_all['NTA_Name'] = df_all.index
        df_all = utils.calculate_kmeans(df_all, value_column, score_column="ESL_all_score")
        df_all['ESL_all_percent'] = np.round([stats.percentileofscore(df_all[value_column].values, x, kind='rank') for x in
                                              np.round(df_all[value_column].values, 6)], 2)
        df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="Value",
                                hazard='All', component='Expected Loss',
                                subcomponent=sub, factor='All',
                                view='Raw Value', view_type='2019 USD', normalization=norm,
                                base_key='NTA_Name', new_key='NTA_Name')
        df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="ESL_all_score",
                                hazard='All', component='Expected Loss',
                                subcomponent=sub, factor='All',
                                view='Score', view_type='1-5 Value', normalization=norm,
                                base_key='NTA_Name', new_key='NTA_Name')
        df_tract = update_tract(df_tract, gdf_shp, df_all, value_column="ESL_all_percent",
                                hazard='All', component='Expected Loss',
                                subcomponent=sub, factor='All',
                                view='Percentile', view_type='Percent', normalization=norm,
                                base_key='NTA_Name', new_key='NTA_Name')

#%% save file
path_tracts = r'C:\temp\TBL_NTA_v1.csv' #params.PATHNAMES.at['TBL_tracts', "Value"]
df_tract_nan = df_tract.copy()
df_tract_nan.replace(nan_value, np.nan, inplace=True)
df_tract_nan.to_csv(path_tracts)

# #%% plot all unique combinations
# df_uniq = df_tract.groupby(['Geography', 'Hazard', 'Component', 'Sub-Component', 'Factor', 'View', 'Type', 'Normalization']).size().reset_index().rename(columns={0:'count'})
# df_uniq.index = np.arange(len(df_uniq))
# #loop through and plot all combinations
# for idx in df_uniq.index:
#     Geography = df_uniq.at[idx, 'Geography']
#     Hazard = df_uniq.at[idx, 'Hazard']
#     Component = df_uniq.at[idx, 'Component']
#     Subcomponent = df_uniq.at[idx, 'Sub-Component']
#     Factor = df_uniq.at[idx, 'Factor']
#     View = df_uniq.at[idx, 'View']
#     Type = df_uniq.at[idx, 'Type']
#     Normalization = df_uniq.at[idx, 'Normalization']
#     df_plot = df_tract.loc[(df_tract.Geography==Geography) & (df_tract.Hazard == Hazard) & (df_tract.Component==Component) &  (df_tract["Sub-Component"]==Subcomponent) & \
#                             (df_tract.Factor==Factor) & (df_tract.View == View) & (df_tract.Type==Type) & (df_tract.Normalization==Normalization) , :]
#     gdf_shp =  gdf_shp.merge(df_plot[['NTA_Name', 'Value']], on='NTA_Name', how='left')
#     fig = plt.figure(figsize=(12, 7))
#     ax = fig.add_subplot(111)
#     if Component == 'Expected Loss':
#         cmap = 'Greens'
#     elif Component == 'Social Vulnerability':
#         cmap = 'Reds'
#     elif Component == 'Resilience Capacity':
#         cmap= 'Oranges'
#     else:
#         cmap='Blues'
#     gdf_shp.plot(ax=ax, column='Value', legend=True, cmap=cmap)
#     plt.title('Geography: {}   Hazard:  {} \nComponent:  {} Subcomponent:  {} Factor:  {} \nView: {}  Type: {} \nNormalization: {}'.format(Geography, Hazard, Component, Subcomponent, Factor, View, Type, Normalization))
#     plt.savefig(r'C:\temp\Tableau_Tables_NTA\{}_{}_{}_{}_{}_{}_{}_{}.png'.format(Geography, Hazard, Component, Subcomponent, Factor, View, Type, Normalization), npi=100)
#     gdf_shp.drop(columns='Value', inplace=True)
#     plt.clf()

#%% make neighborhoods



