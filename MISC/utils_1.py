""" Contains utilities that are used by all scripts """

import numpy as np
import pandas as pd
from MISC import params_1 as params
import os
import scipy.stats as stats
import geopandas as gpd
from sklearn.cluster import KMeans


#%% set home directory
def set_home():
    os.chdir(params.PATHNAMES.at['home', 'Value'])
set_home()

#%% create readme
def write_readme(path_readme, readme_text):
    f = open(path_readme + "\\README.txt", "w")
    f.write(readme_text)
    f.close()

#%% normalize score to scale of 0 to 1 (exclusive)
    #values should be numpy array
def normalize_rank_percentile(values, list_input_null_values=[-999], output_null_value=-999):
    #remove null values from array
    values_trim = np.delete(values, np.where(np.isin(values, list_input_null_values)))
    #add a very high values and low value to prevent 0 and 100 values
    values_trim = np.r_[-1e20, values_trim, 1e20]
    #look through and calculate values_out
    values_out = np.zeros(len(values))
    for i, val in enumerate(values):
        if np.isin(val, list_input_null_values):
            values_out[i] = output_null_value
        else:
            values_out[i] = stats.percentileofscore(values_trim, val, kind='rank')/100
    return values_out

#%% zonal statistics with input shapefile into output shapefile
#path data can either be string or actual data gdf file
#handle null values.
def convert_to_tract_average(path_data, column_name, column_name_out,
                             list_input_null_values=[-999], output_null_value=-999):
    #get data to convert
    if type(path_data)==str:
        gdf_data = gpd.read_file(path_data)
    else:
        gdf_data = path_data.copy()
    epsg = params.SETTINGS.at['epsg', 'Value']
    gdf_data = gdf_data.to_crs(epsg=epsg)
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = gdf_tract.to_crs(epsg=epsg)
    #get spatial union, drop areas with no tract
    gdf_union = gpd.overlay(gdf_tract, gdf_data, how='union')
    gdf_union.dropna(subset=['BCT_txt'], inplace=True)
    #calculate area of each union slice
    gdf_union['area_ft2'] = gdf_union['geometry'].area
    # for each tract, calculate area weighted average of contributions
    # if some values are null, use other values.  If all value are null, assign null
    output_null_value = -999
    list_input_null_values = [-999]
    gdf_tract[column_name_out] = np.zeros(len(gdf_tract))
    for i, idx in enumerate(gdf_tract.index):
        this_BCT = gdf_tract.at[idx, 'BCT_txt']
        # get slices from this tract
        this_gdf_union = gdf_union.loc[gdf_union['BCT_txt'] == this_BCT, :]
        # remove null data values
        this_gdf_union.dropna(subset=[column_name], inplace=True)
        # remove null values based on list
        for null_val in list_input_null_values:
            keep_bool = (this_gdf_union[column_name].values != null_val)
            this_gdf_union = this_gdf_union.loc[keep_bool, :]
        # if nothing left, set tract value to null value
        if len(this_gdf_union) == 0:
            gdf_tract.at[idx, column_name_out] = output_null_value
        # otherise set to spatially weighted average
        else:
            DATA_VALUE_tract_ave = np.average(this_gdf_union[column_name].values,
                                              weights=this_gdf_union['area_ft2'].values)
            gdf_tract.at[idx, column_name_out] = DATA_VALUE_tract_ave
    return gdf_tract

#%% convert value to 2018 dollars using consumer price index (CPI)
def convert_USD(base_value, base_year: int):
    #get target year from parameters
    target_year = params.SETTINGS.at['target_year', 'Value']
    #load CPI index
    path_CPI = params.PATHNAMES.at['CPI_table', 'Value']
    df_CPI = pd.read_excel(path_CPI, skiprows=10,
                           index_col=0, parse_dates=True)
    #get the yearly average
    df_CPI_year = df_CPI.resample('Y').mean()
    df_CPI_year.index = df_CPI_year.index.year
    index_factor = df_CPI_year.at[target_year, 'CPIAUCNS' ] / df_CPI_year.at[base_year, 'CPIAUCNS' ]
    target_value = base_value * index_factor
    return target_value

#%% calculate RCA using pre-processed factors
#all factors should be census tract level results
#list_factors_gdf is a list of the factors as geodataframes
#list_factors_columns is a list of the column names with the relevant scor
#dict_buckets is a coding for the RCA bucket for each factor.  It is blank for now.
def calculate_RCA(list_factor_gdfs, list_factor_columns, dict_buckets={}):
    # get data to convert
    epsg = params.SETTINGS.at['epsg', 'Value']
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = gdf_tract.to_crs(epsg=epsg)
    #open each gdf and take average of all factor columns (for now)
    list_factor_columns_adj = []
    for i, gdf in enumerate(list_factor_gdfs):
        this_score_column = list_factor_columns[i]
        this_score_column_adj = this_score_column + "_{}".format(i)
        list_factor_columns_adj.append(this_score_column_adj)
        gdf[this_score_column_adj] = gdf[this_score_column]
        gdf_tract = gdf_tract.merge(gdf.drop(columns='geometry'), on='BCT_txt')
    #no nan handling for now
    gdf_tract['Score'] = gdf_tract[list_factor_columns_adj].sum(axis=1)
    return gdf_tract

#%% calculate kmeans score and label
def calculate_kmeans(df, data_column, score_column='Score', n_cluster=5):
    kmeans = KMeans(n_clusters=5)
    df['Cluster_ID'] = kmeans.fit_predict(df[[data_column]])
    #make lookup for class label
    df_label = pd.DataFrame()
    df_label['Cluster_ID'] = np.arange(n_cluster)
    df_label['Cluster_Center'] = kmeans.cluster_centers_.flatten()
    df_label.sort_values('Cluster_Center', inplace=True)
    df_label[score_column] = np.arange(1, n_cluster+1)
    #assign score to each cluster
    df_result = df.merge(df_label[['Cluster_ID', score_column]], on='Cluster_ID', how='left')
    return df_result

#%% count number of points (or fraction of) within 1/2 mile of tract
#gdf_data is point layer, column_key is unique id for each point
def calculate_radial_count(gdf_data, column_key, buffer_distance_ft=2640):
    #load gdf_tract
    epsg = params.SETTINGS.at['epsg', 'Value']
    gdf_data = gdf_data.to_crs(epsg=epsg)
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = gdf_tract.to_crs(epsg=epsg)
    gdf_tract['area_ft2'] = gdf_tract['geometry'].area
    #make shapefile with 1/2 mile radius
    gdf_buffer = gdf_data.copy()
    gdf_buffer['geometry'] = gdf_data['geometry'].buffer(distance=buffer_distance_ft)
    #create empty df to fill
    df_fill = pd.DataFrame()
    df_fill['BCT_txt'] = []
    df_fill['Fraction_Covered'] = []
    # loop through each buffer, and add BCT_txt and area filled to list
    print("Calculating.", end='')
    for i, idx in enumerate(gdf_buffer.index):
        this_buffer = gdf_buffer.loc[[idx]]
        this_intersect = gpd.overlay(gdf_tract, this_buffer[[column_key, 'geometry']], how='intersection')
        this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
        this_intersect['Fraction_Covered'] = np.minimum(this_intersect['area_intersect_ft2'] / this_intersect['area_ft2'], 1.0)
        #add to df_fill
        df_fill = df_fill.append(this_intersect[['BCT_txt', 'Fraction_Covered']])
        if i % 500 == 0:
            print(".", end=''),
    print('Done')
    #get the sum  by tract and join
    df_sum = df_fill.groupby(by='BCT_txt').sum()
    gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')
    #fill nan with value 0
    gdf_tract.fillna(0, inplace=True)
    return gdf_tract

def project_gdf(gdf):
    epsg = epsg = params.SETTINGS.at['epsg', 'Value']
    gdf = gdf.to_crs(epsg = epsg)
    return gdf

#start with yearly loss across all NYC, and distribute by population
#return gdf_tract
def distribute_loss_by_pop(USD_loss_2019):
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = project_gdf(gdf_tract)
    gdf_tract.index = np.arange(len(gdf_tract))
    # open population and join
    path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
    df_pop = pd.read_excel(path_population_tract, skiprows=5)
    df_pop.dropna(inplace=True)
    df_pop.rename(columns={2010:'pop_2010'}, inplace=True)
    df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2010 DCP Borough Code'])) + str(int(df_pop.at[x,'2010 Census Tract'])).zfill(6) for x in df_pop.index]
    gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2010']], on='BCT_txt', how='left')
    # distribute cost to each tract by population
    pop_total = gdf_tract['pop_2010'].sum()
    gdf_tract['Loss_USD'] = USD_loss_2019 * gdf_tract['pop_2010'] / pop_total
    return gdf_tract

#assumes gdf_tract has "Loss_USD field to normalize by pop
def normalize_loss_by_population(gdf_tract):
    # open population and join
    path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
    df_pop = pd.read_excel(path_population_tract, skiprows=5)
    df_pop.dropna(inplace=True)
    df_pop.rename(columns={2010:'pop_2010'}, inplace=True)
    df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2010 DCP Borough Code'])) + str(int(df_pop.at[x,'2010 Census Tract'])).zfill(6) for x in df_pop.index]
    gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2010']], on='BCT_txt', how='left')
    # distribute cost to each tract by population
    gdf_tract['Loss_USD'] = gdf_tract['Loss_USD'] / (gdf_tract['pop_2010'])
    gdf_tract.replace([np.inf, -np.inf], np.nan, inplace=True)
    gdf_tract.fillna(0, inplace=True)
    gdf_tract.to_file(r'C:\temp\gdf_tract.shp')
    return gdf_tract

#%% open NYC tract
def get_blank_tract(add_pop=False):
    path_tract = params.PATHNAMES.at['BOUNDARY_tract', 'Value']
    list_exclude = params.HARDCODED.at['list_excluded_tracts', 'Value']
    gdf_tract = gpd.read_file(path_tract)
    bool_keep = [x not in list_exclude for x in gdf_tract['BOROCT']]
    gdf_tract = gdf_tract.loc[bool_keep, :].copy()
    gdf_tract['BCT_txt'] = gdf_tract['BOROCT'].values
    gdf_tract = project_gdf(gdf_tract)
    gdf_tract.index = np.arange(len(gdf_tract))
    if add_pop==True:
        path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
        df_pop = pd.read_excel(path_population_tract, skiprows=5)
        df_pop.dropna(inplace=True)
        df_pop.rename(columns={2010: 'pop_2010'}, inplace=True)
        df_pop['BCT_txt'] = [
            str(int(df_pop.at[x, '2010 DCP Borough Code'])) + str(int(df_pop.at[x, '2010 Census Tract'])).zfill(6) for x
            in df_pop.index]
        gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2010']], on='BCT_txt', how='left')
    return gdf_tract









